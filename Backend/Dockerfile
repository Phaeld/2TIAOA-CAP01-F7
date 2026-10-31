FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 TF_CPP_MIN_LOG_LEVEL=2 TF_USE_LEGACY_KERAS=1
WORKDIR /app
COPY Backend/requirements.txt Backend/requirements-vision.txt ./Backend/
ARG ENABLE_VISION=false
RUN if [ "$ENABLE_VISION" = "true" ]; then pip install --no-cache-dir -r Backend/requirements-vision.txt; else pip install --no-cache-dir -r Backend/requirements.txt; fi
COPY Backend/cardioia ./Backend/cardioia
RUN useradd --create-home app && mkdir -p /app/data && chown -R app:app /app
USER app
ENV PYTHONPATH=/app/Backend CARDIOIA_DB_PATH=/app/data/cardioia.db
CMD ["sh", "-c", "uvicorn cardioia.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
