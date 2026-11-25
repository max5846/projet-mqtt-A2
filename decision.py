# decision.py
# Logique de décision de la Smart House - Équipe E203
import config


class SmartHouse:
    """Gère l'état de la maison et les décisions automatiques"""

    def __init__(self):
        self.alarme_active = False
        self.ventilation_active = False

    def traiter(self, data):
        """
        Prend une mesure (dict) et retourne la liste des actions à effectuer.
        Actions possibles : VENTILATION_ON, VENTILATION_OFF,
                            ALARME_ON, ALARME_OFF
        """
        actions = []

        # --- Gestion de la température (ventilation) ---
        if data["temperature"] > config.SEUIL_TEMP:
            if not self.ventilation_active:
                self.ventilation_active = True
                actions.append("VENTILATION_ON")
        else:
            if self.ventilation_active:
                self.ventilation_active = False
                actions.append("VENTILATION_OFF")

        # --- Gestion de l'intrusion (alarme) ---
        if data["distance"] < config.SEUIL_DISTANCE:
            if not self.alarme_active:
                self.alarme_active = True
                actions.append("ALARME_ON")
        else:
            if self.alarme_active:
                self.alarme_active = False
                actions.append("ALARME_OFF")

        return actions

    def etat(self):
        """Retourne l'état actuel de la maison"""
        return {
            "alarme": self.alarme_active,
            "ventilation": self.ventilation_active
        }