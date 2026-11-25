\# 🏠 Smart House — Équipe E203



Système embarqué connecté basé sur Arduino UNO R4 WiFi, capteur BME680 et caméra, pour la domotique.



\## 📋 Fonctionnalités



\- Acquisition température / humidité / pression / qualité d'air (BME680)

\- Détection d'intrusion (HC-SR04)

\- Décision locale automatique (ventilation, alarme)

\- Communication MQTT sécurisée (TLS 1.3 + certificats)

\- Stockage SQLite

\- Dashboard web responsive (PC + mobile)



\## 🗂 Structure du projet



```text

projet\_smart\_house/

├── app.py                  # Dashboard Flask

├── config.py               # Configuration centrale

├── main\_simule.py          # Programme principal (simulateur)

├── decision.py             # Logique de décision

├── simulateur.py           # Simulateur BME680 + HC-SR04

├── mosquitto.conf          # Configuration broker MQTT

├── .gitignore              # Fichiers exclus de Git

├── README.md               # Ce fichier

├── templates/

│   └── dashboard.html      # Interface web

├── certs/                  # Certificats TLS (non versionnés)

│   └── README.md           # Comment les regénérer

└── data/                   # Base SQLite (non versionnée)

```



\## 🚀 Lancer le projet



1\. \*\*Broker MQTT\*\* :

&#x20;  ```bash

&#x20;  mosquitto -c mosquitto.conf -v

&#x20;  ```



2\. \*\*Programme principal\*\* (simulateur + décision + stockage) :

&#x20;  ```bash

&#x20;  python main\_simule.py

&#x20;  ```



3\. \*\*Dashboard web\*\* :

&#x20;  ```bash

&#x20;  python app.py

&#x20;  ```

&#x20;  Puis ouvrir http://localhost:5000



\## 🔒 Sécurité



\- MQTT sur TLS 1.3 (AES-256-GCM)

\- Certificats client obligatoires (`require\_certificate true`)

\- Clés privées non versionnées (voir `certs/README.md`)



\## 👥 Équipe



\- Étudiant 1 — Électronique / câblage

\- Étudiant 2 — Acquisition + MQTT

\- Étudiant 3 — Automatisation

\- Étudiant 4 — Dashboard + sécurité

