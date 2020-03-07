import json
import logging
from formatter import ReceiptFormatter

import paho.mqtt.client as mqtt
from escpos.config import Config

import printing
import settings

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s", level=logging.DEBUG,
)

logger = logging.getLogger("apis-receipts")
logger.setLevel(logging.DEBUG)
logging.debug(
    "FIXME: Importing the escpos library clobbers logger here for some reason"
)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    logger.info(f"Connected with result code {rc}")

    base_topic = get_base_topic()
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(f"{base_topic}/#")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    logger.debug("Got message:")
    logger.debug(msg.topic + " " + str(msg.payload))

    receipt_printer = get_printer()

    if msg.topic == get_topic("cash_drawer"):
        logger.info("Opening cashdrawer...")
        receipt_printer.cashdraw(settings.CASH_DRAWER_PIN)

    # Commands past here expect a JSON payload:
    try:
        payload = json.loads(msg.payload)
    except json.decoder.JSONDecodeError as e:
        logger.error(e)
        logger.error("Unable to decode message payload from server:")
        logger.error(msg.payload)
        return

    if msg.topic == get_topic("print_cash"):
        print_receipt(receipt_printer, payload, settings.BOTTOM_TEXT_CASH)

    if msg.topic == get_topic("print_credit"):
        print_receipt(receipt_printer, payload, settings.BOTTOM_TEXT_CREDIT)

    # preview badge command chan
    if msg.topic == get_topic("preview"):
        badge_printer = printing.Main(local=True)

        if settings.THEME == "":
            settings.THEME == "apis"
        try:
            badge_printer.nametags(payload.get("badge"), theme=settings.THEME)
            badge_printer.preview()
        except Exception as e:
            logger.error(e)
            logger.error(f"Error on preview")
            logger.error(msg.payload)

    # print badge command chan
    if msg.topic == get_topic("print"):
        badge_printer = printing.Main(local=True)

        if settings.THEME == "":
            settings.THEME == "apis"
        try:
            badge_printer.nametags(payload.get("badges"), theme=settings.THEME)
            badge_printer.printout()
        except Exception as e:
            logger.error(e)
            logger.error(f"Error on print")
            logger.error(msg.payload)

    receipt_printer.close()


def get_topic(command):
    base_topic = get_base_topic()
    return f"{base_topic}/{command}"


def get_base_topic():
    return f"{settings.MQTT_TOPIC}/{settings.STATION_NAME}"


def print_receipt(receipt_printer, payload, bottom_text):
    """
    Example payload:
        {
            "v": 1,
            "event": "Furthemore 2020",
            "line_items": [
                {"item": "Regular Badge", "price": "$45.00"},
                {"item": "Con Book", "price": "$0.00"},
                {"item": "Discount", "price": "-$5.00"}
            ],
            "donations" : {
                "org": {"name": "Furthemore 2020", "price": "$10.00"},
                "charity": {"name": "ALS Society", "price": "$10.00"}
            },
            "total": "$60.00",
            "payment": {
                "type": "Cash",
                "tendered": "$100.00",
                "change": "$40.00",
                "details": "Ref: U4REQT | AID: A0000000031010 | Auth: 025993"
            },
            "reference": "U4REQT"
        }
    """

    receipt_printer.cashdraw(settings.CASH_DRAWER_PIN)

    receipt_printer.image("logo.png")

    event = payload.get("event", "APIS")

    builder = ReceiptFormatter()
    builder.ln()
    builder.center_text(event)
    builder.ln()

    line_items = payload["line_items"]
    for line in line_items:
        builder.format_line_item(line.get("item"), line.get("price"))

    builder.ln()

    donations = payload.get("donations")
    if donations:
        org = donations.get("org")
        if org:
            builder.format_line_item(f"Donation to {org['name']}", org["price"])

        charities = donations.get("charity", [])
        for charity in charities:
            builder.format_line_item(f"Donation to {charity['name']}", charity["price"])

    builder.ln()

    builder.right_text(f"Total Due:  {payload['total']}")
    builder.ln()
    builder.hr()
    builder.ln()

    payment = payload.get("payment")

    if payment:
        builder.format_line_item(payment["type"], payment["tendered"])

        details = payment.get("details")
        if details:
            builder.append(details)

        change = payment.get("change")
        if change:
            builder.right_text(f"Change:  {change}")

    builder.ln()
    builder.hr()
    builder.ln()

    builder.wrap_center(bottom_text)

    print(builder.print())
    receipt_printer.text(builder.pop())

    reference = payload.get("reference")
    if reference:
        receipt_printer.barcode(reference, "CODE39")
        receipt_printer.text("\n")

    receipt_printer.cut()


def get_printer():
    escpos_config = Config()
    receipt_printer = escpos_config.printer()
    return receipt_printer


if __name__ == "__main__":
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.enable_logger(logger=logger)

    try:
        client.username_pw_set(**settings.MQTT_LOGIN)
    except AttributeError:
        logger.debug("No username/password specified - using anonymous access")

    logger.info("Connecting...")
    client.connect(**settings.MQTT_BROKER)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    client.loop_forever()
