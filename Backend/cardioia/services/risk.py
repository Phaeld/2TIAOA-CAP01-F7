"""Adapt phase-six model and protocol agents; preserve their numerical outputs."""
from datetime import datetime, timezone

from ..config import ASSETS, DISCLAIMER
from ..legacy.agent_ml import MLPredictionAgent
from ..legacy.protocol_agent import ProtocolAgent

# Fixed simulation scenario, never inferred from a single patient's sensor.
DEMO_CONTEXT = {
    "middle_ages": 62, "system_load": 65, "waiting_time": 30,
    "average_spo2": 97, "systolic_bp": 120,
    "event_density": 3, "events_24h": 2, "resource_availability": 70,
}


class RiskService:
    def __init__(self):
        self.model = MLPredictionAgent(ASSETS / "risk_model.joblib")
        self.protocols = ProtocolAgent()

    def predict(self, case):
        prediction = self.model.predict(case)
        protocols = self.protocols.analyze(prediction)
        return {
            **prediction,
            "suggested_protocols": protocols["suggested_protocols"],
            "source": "phase6_random_forest",
            "scope": "synthetic_operational_risk",
            "disclaimer": DISCLAIMER,
            "pipeline": ["MLPredictionAgent", "ProtocolAgent", "ResponsePlanner"],
            "summary": f"Cenário operacional simulado: classe {prediction['risk_level']}; {protocols['protocol_count']} regras acionadas.",
        }

    def ingest(self, reading):
        case = {**DEMO_CONTEXT, "average_hr": reading.heart_rate_bpm, "temperature": reading.temperature_c}
        supplied = ["average_hr", "temperature"]
        if reading.spo2_percent is not None:
            case["average_spo2"] = reading.spo2_percent
            supplied.append("average_spo2")
        if reading.systolic_bp is not None:
            case["systolic_bp"] = reading.systolic_bp
            supplied.append("systolic_bp")
        prediction = self.predict(case)
        alerts = []
        # Same phase-three rules, separated from the hospital-level ML result.
        for matches, code, severity, text in [
            (reading.temperature_c > 38, "FEVER", "HIGH", "Temperatura acima de 38 °C na simulação."),
            (reading.heart_rate_bpm > 120, "TACHYCARDIA", "HIGH", "Frequência acima de 120 bpm na simulação."),
            (not reading.movement_detected, "NO_MOVEMENT", "MEDIUM", "Sensor não informou movimento."),
            (reading.emergency_button_pressed, "EMERGENCY_BUTTON", "CRITICAL", "Botão de emergência acionado na simulação."),
        ]:
            if matches:
                alerts.append({"type": code, "severity": severity, "message": text})
        severity = next((s for s in ["CRITICAL", "HIGH", "MEDIUM"] if any(a["severity"] == s for a in alerts)), "NORMAL")
        feedback = "red" if severity in ("HIGH", "CRITICAL") else "yellow" if severity == "MEDIUM" else "green"
        now = datetime.now(timezone.utc).isoformat()
        return {
            "event_id": reading.event_id, "device_id": reading.device_id,
            "patient_id": reading.patient_id, "schema_version": "1.0",
            "captured_at": reading.timestamp.isoformat() if reading.timestamp else now,
            "received_at": now, "duplicate": False,
            "vitals": reading.model_dump(mode="json"),
            "sensor_alerts": {"risk_level": severity, "alerts": alerts},
            "prediction": prediction,
            "feature_provenance": {key: "sensor_simulado" if key in supplied else "contexto_sintetico_fixo" for key in case},
            "feedback": {"led": feedback, "label": severity},
            "disclaimer": DISCLAIMER,
        }
