import logging

import escpos
import paho.mqtt.client as mqtt

import settings

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)

logger = logging.getLogger("apis-receipts")


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    logger.info(f"Connected with result code {rc}")

    base_topic = get_base_topic()
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(f"{base_topic}/#")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    logger.debug(msg.topic + " " + str(msg.payload))

    if msg.topic == get_topic("cash_drawer"):
        receipt_printer.cashdraw(settings.CASH_DRAWER_PIN)

    if msg.topic == get_topic("print_cash"):
        print_cash(msg.payload)


def get_topic(command):
    base_topic = get_base_topic()
    return f"{base_topic}/{command}"


def get_base_topic():
    return f"{settings.MQTT_TOPIC}/{settings.STATION_NAME}"


def print_cash(payload):
    pass


if __name__ == "__main__":
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.enable_logger(logger=None)

    try:
        client.username_pw_set(**settings.MQTT_LOGIN)
    except KeyError:
        pass

    logger.info("Connecting...")
    client.connect(**settings.MQTT_BROKER)

    escpos_config = escpos.config.Config()
    receipt_printer = escpos_config.printer()

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    client.loop_forever()
