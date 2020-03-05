import json
import logging

import paho.mqtt.client as mqtt

import settings
import printing

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s", level=logging.DEBUG,
)

logger = logging.getLogger("apis-receipts")
logger.setLevel(logging.DEBUG)


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

    badge_printer = printing.Main(local=True)

    # Commands past here expect a JSON payload:
    try:
        payload = json.loads(msg.payload)
    except json.decoder.JSONDecodeError as e:
        logger.error(e)
        logger.error("Unable to decode message payload from server:")
        logger.error(msg.payload)
        return

    # preview command chan
    if msg.topic == get_topic("preview"):
        # code for preview
        print("not done")

    # print command chan
    if msg.topic == get_topic("print"):
        if settings.THEME == "":
            settings.THEME == "apis"
        try:
            badge_printer.nametags(payload, theme=settings.THEME)
        except Exception as e:
            logger.error(e)
            logger.error(f"Error on print")
            logger.error(msg.payload)


def get_topic(command):
    base_topic = get_base_topic()
    return f"{base_topic}/{command}"


def get_base_topic():
    return f"{settings.BADGE_MQTT_TOPIC}/{settings.STATION_NAME}"


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
