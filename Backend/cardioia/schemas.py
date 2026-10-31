from datetime import datetime, timezone, timedelta
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, StrictBool, field_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False, str_strip_whitespace=True)


class Login(StrictModel):
    email: str = Field(min_length=3, max_length=160)
    password: str = Field(min_length=1, max_length=256)


class Telemetry(StrictModel):
    schema_version: Literal["1.0"] = "1.0"
    event_id: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_-]+$")
    device_id: str = Field(min_length=1, max_length=64)
    patient_id: str = Field(min_length=1, max_length=64)
    temperature_c: float = Field(ge=10, le=50)
    heart_rate_bpm: int = Field(ge=30, le=240, strict=True)
    movement_detected: StrictBool = True
    emergency_button_pressed: StrictBool = False
    spo2_percent: float | None = Field(default=None, ge=50, le=100)
    systolic_bp: float | None = Field(default=None, ge=50, le=250)
    timestamp: datetime | None = None

    @field_validator("timestamp")
    @classmethod
    def valid_timestamp(cls, value):
        if value is None:
            return value
        if value.tzinfo is None:
            raise ValueError("timestamp precisa incluir timezone (Z ou offset)")
        now = datetime.now(timezone.utc)
        if value > now + timedelta(minutes=5) or value < now - timedelta(days=1):
            raise ValueError("timestamp deve estar entre 24h atrás e 5min à frente")
        return value.astimezone(timezone.utc)


class RiskCase(StrictModel):
    middle_ages: float = Field(ge=18, le=100)
    system_load: float = Field(ge=0, le=100)
    waiting_time: float = Field(ge=0, le=300)
    average_hr: float = Field(ge=30, le=240)
    average_spo2: float = Field(ge=50, le=100)
    systolic_bp: float = Field(ge=50, le=250)
    temperature: float = Field(ge=10, le=50)
    event_density: float = Field(ge=0, le=100)
    events_24h: float = Field(ge=0, le=1000)
    resource_availability: float = Field(ge=0, le=100)


class TextRequest(StrictModel):
    message: str = Field(min_length=3, max_length=4000)
