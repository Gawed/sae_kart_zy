import paho.mqtt.client as mqtt
import logging

logging.basicConfig(level=logging.DEBUG)

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")

client = mqtt.Client()
client.on_connect = on_connect
client.connect("192.168.1.205", 1883, 60)
client.loop_forever()
