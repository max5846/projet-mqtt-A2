# app.py
# Dashboard Flask pour Smart House E203
import json
import sqlite3
import ssl
import threading

import paho.mqtt.client as mqtt
from flask import Flask, jsonify, render_template

import config

app = Flask(__name__)

# État global partagé
derniere_mesure = {}
dernier_etat = {"alarme": False, "ventilation": False}
dernieres_alertes = []


# ---------- MQTT ----------
def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"[MQTT] Connecté (code={reason_code})")
    client.subscribe("smartHouse/E203/#", qos=1)


def on_message(client, userdata, msg):
    global derniere_mesure, dernier_etat, dernieres_alertes
    try:
        payload = json.loads(msg.payload.decode())
    except Exception:
        return

    if msg.topic.endswith("/mesures"):
        derniere_mesure = payload
    elif msg.topic.endswith("/etat"):
        dernier_etat = payload
    elif msg.topic.endswith("/alertes"):
        dernieres_alertes = payload.get("actions", [])


def demarrer_mqtt():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="E203_dashboard")
    if config.USE_TLS:
        client.tls_set(
            ca_certs=config.CA_CERT,
            certfile=config.CLIENT_CERT,
            keyfile=config.CLIENT_KEY,
            tls_version=ssl.PROTOCOL_TLSv1_2,
        )
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(config.MQTT_BROKER, config.MQTT_PORT)
    client.loop_forever()


# ---------- Base de données ----------
def get_historique(limit=50):
    try:
        conn = sqlite3.connect("data/smartHouse.db")
        rows = conn.execute("""
            SELECT temperature, humidite, pression, qualite_air, distance, timestamp
            FROM mesures ORDER BY id DESC LIMIT ?
        """, (limit,)).fetchall()
        conn.close()
        rows.reverse()
        return [
            {
                "temperature": r[0], "humidite": r[1], "pression": r[2],
                "qualite_air": r[3], "distance": r[4], "timestamp": r[5],
            }
            for r in rows
        ]
    except Exception as e:
        print("Erreur DB:", e)
        return []


# ---------- Routes ----------
@app.route("/")
def index():
    return render_template("dashboard.html")


@app.route("/api/mesures")
def api_mesures():
    return jsonify(derniere_mesure)


@app.route("/api/etat")
def api_etat():
    return jsonify({"etat": dernier_etat, "alertes": dernieres_alertes})


@app.route("/api/historique")
def api_historique():
    return jsonify(get_historique(50))


# ---------- Main ----------
if __name__ == "__main__":
    threading.Thread(target=demarrer_mqtt, daemon=True).start()
    print("Dashboard sur http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)