"""
Project: CardioIA - Go Beyond 1 (REST Email)
Linguage: Python
API: REST / Flask
AUTHOR: Raphael da Silva RM: 561452
GROUP: São Paulo e Interior
"""

# Import libraries
from app.config import Config
from app.models.vital_signs import VitalSigns

class RiskAnalysisService:
    @staticmethod
    def analyze(vital_signs: VitalSigns) -> dict:
        # List of alerts detected locally by the API.
        alerts = []

        # Rule 1: Fever
        if vital_signs.temperature_c > Config.MAX_TEMPERATURE_C:
            alerts.append({
                "type": "FEVER",
                "severity": "HIGH",
                "message": f"Temperatura acima do limite: {vital_signs.temperature_c} ºC"
            })
        
        # Rule 2: tachycardia
        if vital_signs.heart_rate_bpm > Config.MAX_HEART_RATE_BPM:
            alerts.append({
                "type": "TACHYCARDIA",
                "severity": "HIGH",
                "message": f"Taquicardia detectada: {vital_signs.heart_rate_bpm} BPM"
            })

        # Rule 3: Absence of movement
        if not vital_signs.movement_detected:
            alerts.append({
                "type": "NO_MOVEMENT",
                "severity": "MEDIUM",
                "message": "Ausência de movimento detectada"
            })
        
        # Rule 4: Emergency button
        if vital_signs.emergency_button_pressed:
            alerts.append({
                "type": "EMERGENCY_BUTTON",
                "severity": "CRITICAL",
                "message": "Botão de emergência acionado pelo paciente"
            })
        
        # Defines the overall level of the event
        has_critical_alert = any(alert["severity"] == "CRITICAL" for alert in alerts)
        has_high_alert = any(alert["severity"] == "HIGH" for alert in alerts)

        if has_critical_alert:
            general_risk_level = "CRITICAL"
        elif has_high_alert:
            general_risk_level = "HIGH"
        elif alerts:
            general_risk_level = "MEDIUM"
        else:
            general_risk_level = "NORMAL"

        return {
            "risk_level": general_risk_level,
            "alert_count": len(alerts),
            "alerts": alerts
        }