FROM python:3.13.5-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/backend \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements-web.txt ./
RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements-web.txt

COPY backend ./backend
COPY migrations ./migrations
COPY frontend ./frontend
COPY alembic.ini ./
COPY scripts ./scripts

EXPOSE 8080

# Railway API service default. The worker overrides the command in its service settings.
CMD ["/bin/sh", "-c", "alembic upgrade head && exec uvicorn orstudio.web_api:app --host 0.0.0.0 --port ${PORT:-8080} --proxy-headers --forwarded-allow-ips=*"]
