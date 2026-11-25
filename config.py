# config.py
# Fichier de configuration central du projet Smart House - Équipe E203

# --- Broker MQTT ---
MQTT_BROKER = "localhost"
MQTT_PORT = 8883          # 1883 = sans TLS (test) | 8883 = avec TLS (final)
USE_TLS = True            # False = pas de TLS | True = TLS activé

# --- Topics MQTT ---
MQTT_TOPIC_MESURES = "smartHouse/E203/mesures"
MQTT_TOPIC_ALERTES = "smartHouse/E203/alertes"
MQTT_TOPIC_ETAT    = "smartHouse/E203/etat"

# --- Certificats TLS (utilisés seulement si USE_TLS = True) ---
CA_CERT     = "certs/ca.crt"
CLIENT_CERT = "certs/client.crt"
CLIENT_KEY  = "certs/client.key"

# --- Seuils de décision ---
SEUIL_TEMP     = 24.0   # °C : au-dessus → ventilation ON
SEUIL_DISTANCE = 50.0   # cm : en-dessous → alarme intrusion

# --- Fréquence d'acquisition ---
INTERVALLE = 5          # secondes (cahier des charges : ≤ 5 s)

# --- Caméra ---
USE_REAL_CAMERA = False                              # False = image simulée | True = vraie caméra
CAMERA_URL = "http://192.168.1.XX/stream"            # URL du flux MJPEG (Arducam / ESP32-CAM)
CAMERA_FALLBACK_IMAGE = "static/camera_demo.png"     # Image affichée si mode simulé

# --- Seuils configurables (fichier partagé avec main_simule.py) ---
SEUILS_FILE = "data/seuils.json"