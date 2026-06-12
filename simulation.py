import json
import time
import random
from datetime import datetime
import paho.mqtt.client as mqtt

EMQX_HOST = "localhost"
EMQX_PORT = 1883
MQTT_TOPIC = "capteurs/particules"

client = mqtt.Client(client_id="capteur-publisher")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Connected to EMQX at {EMQX_HOST}:{EMQX_PORT}")
    else:
        print(f"Connection failed with code {rc}")

def on_publish(client, userdata, mid):
    print(f"Message published (mid={mid})")

client.on_connect = on_connect
client.on_publish = on_publish

client.connect(EMQX_HOST, EMQX_PORT, keepalive=60)
client.loop_start()

PARTICULES = [
    {"particule": "Ammoniac",          "notation": "NH3"},
    {"particule": "Azote",             "notation": "N2"},
    {"particule": "Dioxide de Carbone","notation": "CO2"},
    {"particule": "Monoxide de Carbone","notation": "CO"},
    {"particule": "Dioxyde de Soufre", "notation": "SO2"},
]

def send_capteur(id, latitude, longitude, zone, status, particule, notation, concentration):
    payload = {
        "schema": {
            "type": "struct",
            "fields": [
                {"field": "id",         "type": "int32",  "optional": False},
                {"field": "latitude",   "type": "double", "optional": True},
                {"field": "longitude",  "type": "double", "optional": True},
                {"field": "zone",       "type": "string", "optional": True},
                {"field": "status",     "type": "string", "optional": True},
                {"field": "event_type", "type": "string", "optional": True},
                {"field": "particule",  "type": "string", "optional": True},
                {"field": "notation",   "type": "string", "optional": True},
                {"field": "timestamp",  "type": "string", "optional": True},
                {"field": "concentration",     "type": "double", "optional": True},
            ],
            "optional": False,
            "name": "capteur"
        },
        "payload": {
            "id":         id,
            "latitude":   latitude,
            "longitude":  longitude,
            "zone":       zone,
            "status":     status,
            "event_type": "particle-update-events",
            "particule":  particule,
            "notation":   notation,
            "timestamp":  str(datetime.now()),
            "concentration":   concentration,
        }
    }
    client.publish(MQTT_TOPIC, json.dumps(payload), qos=1)
    print(f"Published: {notation} = {concentration} @ {zone}")

try:
    i = 1
    while True:
        p = random.choice(PARTICULES)
        send_capteur(
            id        = i,
            latitude  = round(random.uniform(14.0, 15.0), 4),
            longitude = round(random.uniform(16.5, 17.5), 4),
            zone      = random.choice(["Diamniadio", "Sébikotane", "Bargny"]),
            status    = "ACTIVE",
            particule = p["particule"],
            notation  = p["notation"],
            concentration   = round(random.uniform(0.1, 100.0), 2),
        )
        i += 1
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Stopping...")
    client.loop_stop()
    client.disconnect()
