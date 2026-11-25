# simulateur.py
# Simule le BME680 et le HC-SR04 en attendant le matériel
import random
import time


def lire_bme680_simule():
    """Simule le capteur BME680 avec des valeurs réalistes"""
    return {
        "temperature": round(random.uniform(18.0, 30.0), 2),   # °C
        "humidite":    round(random.uniform(30.0, 70.0), 2),   # %
        "pression":    round(random.uniform(1000.0, 1025.0), 2),  # hPa
        "qualite_air": round(random.uniform(50.0, 300.0), 2),  # résistance gaz
    }


def lire_hcsr04_simule():
    """Simule un HC-SR04 : distance variable, avec 10% de chance d'intrusion"""
    if random.random() < 0.10:
        # Intrusion simulée : distance < 50 cm
        return round(random.uniform(10.0, 49.0), 2)
    # Pas d'intrusion : distance > 50 cm
    return round(random.uniform(50.0, 300.0), 2)


def generer_mesure():
    """Retourne un dictionnaire complet de mesure avec timestamp"""
    data = lire_bme680_simule()
    data["distance"] = lire_hcsr04_simule()
    data["timestamp"] = time.time()
    return data


if __name__ == "__main__":
    print("=== Test du simulateur (5 mesures) ===")
    for i in range(5):
        mesure = generer_mesure()
        print(f"Mesure {i+1} : {mesure}")
        time.sleep(1)