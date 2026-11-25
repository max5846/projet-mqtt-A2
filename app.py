# app.py
# Dashboard Flask pour Smart House E203
import json
import sqlite3
import ssl
import struct
import threading
import time
import urllib.request
import zlib
import os

import paho.mqtt.client as mqtt
from flask import Flask, Response, jsonify, render_template, request

import config

app = Flask(__name__)

# URL du flux caméra (définie dans config.py)
CAMERA_URL = config.CAMERA_URL

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


# ---------- Caméra : simulation ----------
def generer_image_simulee():
    """Génère un PNG 320x240 avec un carré qui bouge (sans Pillow)."""
    w, h = 320, 240
    t = int(time.time()) % 8
    offset = t * 20

    raw = b""
    for y in range(h):
        raw += b"\x00"
        for x in range(w):
            r = int(30 + 40 * (x / w))
            g = int(40 + 50 * (y / h))
            b = int(60 + 30 * (x / w))
            if offset <= x < offset + 60 and 80 <= y < 140:
                r, g, b = 220, 80, 80
            raw += bytes([r, g, b])

    def chunk(typ, data):
        c = struct.pack(">I", len(data)) + typ + data
        c += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
        return c

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw))
    png += chunk(b"IEND", b"")
    return png


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


@app.route("/video_feed")
def video_feed():
    # Mode simulé
    if not config.USE_REAL_CAMERA:
        return Response(generer_image_simulee(), mimetype="image/png")

    # Mode réel : proxy MJPEG
    try:
        stream = urllib.request.urlopen(CAMERA_URL, timeout=5)
        content_type = stream.headers.get(
            "Content-Type", "multipart/x-mixed-replace; boundary=frame"
        )

        def generate():
            try:
                while True:
                    chunk = stream.read(4096)
                    if not chunk:
                        break
                    yield chunk
            finally:
                stream.close()

        return Response(generate(), mimetype=content_type)
    except Exception as e:
        print("Erreur caméra:", e)
        return "Caméra hors ligne", 503

# ---------- Seuils ----------
def lire_seuils():
    try:
        with open(config.SEUILS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"seuil_temp": config.SEUIL_TEMP, "seuil_distance": config.SEUIL_DISTANCE}


def ecrire_seuils(seuils):
    with open(config.SEUILS_FILE, "w", encoding="utf-8") as f:
        json.dump(seuils, f, indent=2)


@app.route("/api/seuils", methods=["GET", "POST"])
def api_seuils():
    if request.method == "POST":
        data = request.get_json()
        seuils = {
            "seuil_temp": float(data.get("seuil_temp", config.SEUIL_TEMP)),
            "seuil_distance": float(data.get("seuil_distance", config.SEUIL_DISTANCE)),
        }
        ecrire_seuils(seuils)
        return jsonify({"ok": True, "seuils": seuils})
    return jsonify(lire_seuils())


# ---------- Main ----------
if __name__ == "__main__":
    threading.Thread(target=demarrer_mqtt, daemon=True).start()
    mode = "simulée" if not config.USE_REAL_CAMERA else "réelle"
    print(f"Dashboard sur http://localhost:5000 (caméra {mode})")
    app.run(host="0.0.0.0", port=5000, debug=False)