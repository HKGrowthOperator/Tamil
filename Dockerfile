# Tamil.de News-Radar – ein Container für Coolify (Build-Pack „Dockerfile“, Port 3000).
# Cockpit, Scan alle 3 Minuten, Worker der Redaktion v2, Digest und Sicherung laufen in `python -m news_radar dienst`.
# Persistent Storage in Coolify auf /app/data legen (Datenbank, Bilder, Sicherungen) – sonst ist beim Redeploy alles weg.
# Variablen: siehe README, Abschnitt „Coolify“.
FROM python:3.13-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    RADAR_DATA_DIR=/app/data \
    PORT=3000 \
    TZ=Europe/Berlin

WORKDIR /app
# curl braucht der Healthcheck von Coolify (ohne curl/wget rollt Coolify jeden Deploy zurück)
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --system --uid 1000 --create-home --home-dir /home/radar radar

COPY requirements.txt .
RUN pip install -r requirements.txt tzdata

COPY sources.toml .
COPY news_radar ./news_radar
RUN mkdir -p /app/data && chown radar:radar /app/data

# Der Dienst startet als root, übergibt /app/data (Coolify-Volumes gehören anfangs root) an `radar` und gibt die
# Rechte dann ab – Cockpit, Scan und Worker laufen nie als root.
VOLUME /app/data
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
  CMD curl -fsS "http://127.0.0.1:${PORT:-3000}/gesund" > /dev/null || exit 1

CMD ["python", "-m", "news_radar", "dienst"]
