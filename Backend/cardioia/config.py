from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
ASSETS = Path(__file__).resolve().parent / "assets"
DISCLAIMER = "Protótipo acadêmico com dados simulados. Não é diagnóstico nem orientação médica."


@dataclass(frozen=True)
class Settings:
    secret: str
    password: str
    device_key: str
    email: str = "demo@cardioia.local"
    device_id: str = "esp32-001"
    patient_id: str = "demo-001"
    db_path: str = "./data/cardioia.db"
    origins: tuple[str, ...] = ("http://localhost:5173",)
    gemini_key: str = ""
    gemini_model: str = "gemini-3.5-flash-lite"
    vision_enabled: bool = False

    def validate(self):
        if len(self.secret) < 32 or len(self.password) < 12 or len(self.device_key) < 24:
            raise RuntimeError("Configure credenciais fortes no .env: python scripts/setup_local.py")

    @classmethod
    def from_env(cls):
        load_dotenv(ROOT / ".env")
        return cls(
            secret=os.getenv("CARDIOIA_SECRET", ""),
            password=os.getenv("CARDIOIA_DEMO_PASSWORD", ""),
            device_key=os.getenv("CARDIOIA_DEVICE_KEY", ""),
            email=os.getenv("CARDIOIA_DEMO_EMAIL", "demo@cardioia.local"),
            device_id=os.getenv("CARDIOIA_DEVICE_ID", "esp32-001"),
            patient_id=os.getenv("CARDIOIA_PATIENT_ID", "demo-001"),
            db_path=os.getenv("CARDIOIA_DB_PATH", str(ROOT / "data/cardioia.db")),
            origins=tuple(x.strip() for x in os.getenv("CARDIOIA_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if x.strip()),
            gemini_key=os.getenv("GEMINI_API_KEY", ""),
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
            vision_enabled=os.getenv("CARDIOIA_VISION_ENABLED", "false").lower() == "true",
        )
