# main_simule.py
# Programme principal : acquisition simulée + décision + envoi MQTT + stockage SQLite
import time
import json
import sqlite3
import ssl
import paho.mqtt.client as mqtt
import os

import config
from simulateur import generer_mesure
from decision import SmartHouse


# ---------- Base de données SQLite ----------
def init_db():
    conn = sqlite3.connect("data/smartHouse.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS mesures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperature REAL,
            humidite REAL,
            pression REAL,
            qualite_air REAL,
            distance REAL,
            timestamp REAL
        )
    """)
    conn.commit()
    conn.close()


def stocker(data):
    conn = sqlite3.connect("data/smartHouse.db")
    conn.execute("""
        INSERT INTO mesures (temperature, humidite, pression, qualite_air, distance, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (data["temperature"], data["humidite"], data["pression"],
          data["qualite_air"], data["distance"], data["timestamp"]))
    conn.commit()
    conn.close()


# ---------- MQTT ----------
def creer_client():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="E203_simulateur")
    if config.USE_TLS:
        client.tls_set(
            ca_certs=config.CA_CERT,
            certfile=config.CLIENT_CERT,
            keyfile=config.CLIENT_KEY,
            tls_version=ssl.PROTOCOL_TLSv1_2
        )
    client.connect(config.MQTT_BROKER, config.MQTT_PORT)
    client.loop_start()
    return client


# ---------- Main ----------
def main():
    print("=== Smart House E203 - Mode SIMULÉ ===")
    print(f"Broker : {config.MQTT_BROKER}:{config.MQTT_PORT} (TLS={config.USE_TLS})")

    init_db()
    client = creer_client()
    maison = SmartHouse()

    try:
        while True:
            # Relire les seuils (peuvent avoir été modifiés depuis le dashboard)
            try:
                with open(config.SEUILS_FILE, "r", encoding="utf-8") as f:
                    seuils = json.load(f)
                config.SEUIL_TEMP = seuils["seuil_temp"]
                config.SEUIL_DISTANCE = seuils["seuil_distance"]
            except Exception:
                pass  # Garde les valeurs par défaut

            data = generer_mesure()
            # ... le reste ne change pas

            # 1. Publication des mesures
            client.publish(config.MQTT_TOPIC_MESURES, json.dumps(data), qos=1)

            # 2. Décision locale
            actions = maison.traiter(data)

            # 3. Publication des alertes si besoin
            if actions:
                client.publish(config.MQTT_TOPIC_ALERTES,
                               json.dumps({"actions": actions, "timestamp": data["timestamp"]}),
                               qos=1)

            # 4. Publication de l'état
            client.publish(config.MQTT_TOPIC_ETAT, json.dumps(maison.etat()), qos=1)

            # 5. Stockage local
            stocker(data)

            # Affichage console
            print(f"[{time.strftime('%H:%M:%S')}] "
                  f"T={data['temperature']}°C | H={data['humidite']}% | "
                  f"dist={data['distance']}cm | actions={actions}")

            time.sleep(config.INTERVALLE)

    except KeyboardInterrupt:
        print("\nArrêt du programme.")
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()