from collections import defaultdict, deque
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
import hashlib
import secrets
import time
from typing import Literal
from uuid import uuid4

import httpx
import jwt
from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import DISCLAIMER, Settings
from .database import Database, EventConflict
from .schemas import Login, RiskCase, Telemetry, TextRequest
from .services.chat import ChatService
from .services.risk import RiskService
from .services.text import TextService
from .services.vision import VisionService


class BodyLimit:
    """Bound all incoming bodies, including chunked uploads."""
    def __init__(self, app, maximum=6 * 1024 * 1024):
        self.app, self.maximum = app, maximum

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        chunks, size = [], 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            size += len(message.get("body", b""))
            if size > self.maximum:
                return await JSONResponse({"detail": "Corpo da requisição excede 6 MB."}, 413)(scope, receive, send)
            chunks.append(message)
            if not message.get("more_body", False):
                break
        async def replay():
            return chunks.pop(0) if chunks else await receive()
        await self.app(scope, replay, send)


def create_app(settings=None):
    config = settings or Settings.from_env()
    limiter = defaultdict(deque)

    @asynccontextmanager
    async def lifespan(app):
        config.validate()
        app.state.db = Database(config.db_path)
        app.state.risk = RiskService()
        app.state.text = TextService()
        app.state.chat = ChatService(config, app.state.text)
        app.state.vision = VisionService(config.vision_enabled)
        yield

    app = FastAPI(title="CardioIA • Fase 7", version="1.0.0", lifespan=lifespan,
                  description="API acadêmica. Somente dados simulados. Contrato de integração Web, Mobile e Wokwi.")
    app.add_middleware(BodyLimit)
    app.add_middleware(CORSMiddleware, allow_origins=list(config.origins), allow_methods=["GET", "POST"],
                       allow_headers=["Authorization", "Content-Type", "X-Device-Key"])
    bearer = HTTPBearer(auto_error=False)
    salt = secrets.token_bytes(16)
    password_hash = hashlib.pbkdf2_hmac("sha256", config.password.encode(), salt, 200_000)

    def rate_limit(bucket, limit, window=60):
        now = time.monotonic()
        for key in list(limiter):
            if not limiter[key] or limiter[key][-1] < now-window:
                del limiter[key]
        queue = limiter[bucket]
        while queue and queue[0] < now-window:
            queue.popleft()
        if len(queue) >= limit:
            raise HTTPException(429, "Muitas requisições. Tente novamente em um minuto.", headers={"Retry-After": str(window)})
        queue.append(now)

    def user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)):
        if not credentials:
            raise HTTPException(401, "Faça login para continuar.")
        try:
            claims = jwt.decode(credentials.credentials, config.secret, algorithms=["HS256"],
                                audience="cardioia", issuer="cardioia-api", options={"require": ["exp", "sub", "iat"]})
            if claims["sub"] != config.email:
                raise ValueError()
            return claims["sub"]
        except (jwt.InvalidTokenError, ValueError):
            raise HTTPException(401, "Sessão inválida ou expirada.") from None

    def device(x_device_key: str | None = Header(default=None)):
        if not x_device_key or not secrets.compare_digest(x_device_key, config.device_key):
            raise HTTPException(401, "Chave do dispositivo inválida.")
        rate_limit("device", 120)

    def ingest(reading):
        if reading.device_id != config.device_id or reading.patient_id != config.patient_id:
            raise HTTPException(403, "Dispositivo ou paciente fora do escopo desta chave.")
        result = app.state.risk.ingest(reading)
        try:
            return app.state.db.store(reading.model_dump(mode="json"), result)
        except EventConflict:
            raise HTTPException(409, "event_id já usado com outro conteúdo.") from None

    @app.get("/health")
    def health():
        app.state.db.history(1)
        return {"status": "ok", "version": "1.0.0", "risk_model": "loaded",
                "chat": "gemini_configured" if config.gemini_key else "local_fallback",
                "vision": "loaded" if app.state.vision.model is not None else "configured" if config.vision_enabled else "disabled"}

    @app.post("/api/v1/auth/login")
    def login(data: Login, request: Request):
        rate_limit("login:" + (request.client.host if request.client else "unknown"), 10)
        given = hashlib.pbkdf2_hmac("sha256", data.password.encode(), salt, 200_000)
        if not secrets.compare_digest(given, password_hash) or data.email.lower() != config.email.lower():
            raise HTTPException(401, "E-mail ou senha inválidos.")
        now = datetime.now(timezone.utc)
        token = jwt.encode({"sub": config.email, "iat": now, "exp": now+timedelta(hours=2),
                            "iss": "cardioia-api", "aud": "cardioia"}, config.secret, algorithm="HS256")
        return {"access_token": token, "token_type": "bearer", "expires_in": 7200}

    @app.get("/api/v1/auth/me")
    def me(email=Depends(user)):
        return {"email": email, "patient_id": config.patient_id, "mode": "academic_demo"}

    @app.post("/api/v1/readings", dependencies=[Depends(device)])
    def receive(reading: Telemetry):
        return ingest(reading)

    @app.get("/api/v1/readings", dependencies=[Depends(user)])
    def history(limit: int = Query(default=30, ge=1, le=200)):
        return {"items": app.state.db.history(limit)}

    @app.get("/api/v1/dashboard", dependencies=[Depends(user)])
    def dashboard():
        readings = app.state.db.history(30)
        latest = readings[0] if readings else None
        age = (datetime.now(timezone.utc)-datetime.fromisoformat(latest["captured_at"])).total_seconds() if latest else None
        return {"patient": {"id": config.patient_id, "name": "Paciente demonstração", "synthetic": True},
                "latest": latest, "history": readings, "stale": age is None or age > 30,
                "age_seconds": round(max(age, 0)) if age is not None else None,
                "chat_provider": "gemini" if config.gemini_key else "local_fallback", "disclaimer": DISCLAIMER}

    @app.post("/api/v1/demo/reading", dependencies=[Depends(user)])
    def demo(scenario: Literal["normal", "alert", "emergency"] = "normal"):
        reading = Telemetry(event_id="demo-"+uuid4().hex, device_id=config.device_id, patient_id=config.patient_id,
                            temperature_c=39.1 if scenario == "alert" else 36.6,
                            heart_rate_bpm=132 if scenario == "alert" else 76,
                            emergency_button_pressed=scenario == "emergency")
        return ingest(reading)

    @app.post("/api/v1/risk", dependencies=[Depends(user)])
    def predict(case: RiskCase):
        return app.state.risk.predict(case.model_dump())

    @app.post("/api/v1/symptoms", dependencies=[Depends(user)])
    def symptoms(data: TextRequest):
        return app.state.text.analyze(data.message)

    @app.post("/api/v1/chat", dependencies=[Depends(user)])
    async def chat(data: TextRequest):
        rate_limit("chat", 12)
        readings = app.state.db.history(1)
        try:
            return await app.state.chat.reply(data.message, readings[0] if readings else None)
        except (httpx.HTTPError, ValueError, KeyError):
            raise HTTPException(503, "Gemini indisponível. Confira a chave, o modelo e a cota no backend.") from None

    @app.post("/api/v1/vision", dependencies=[Depends(user)])
    def vision(image: UploadFile):
        rate_limit("vision", 6)
        try:
            return app.state.vision.predict(image.file.read(5*1024*1024+1))
        except ValueError as error:
            raise HTTPException(422, str(error)) from None
        except (RuntimeError, ImportError):
            raise HTTPException(503, "Modelo de visão indisponível. Confira a configuração do backend.") from None

    return app


app = create_app()
