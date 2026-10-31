FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Instala o FFmpeg necessário para reprodução de áudio e conversão via yt-dlp
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg libffi-dev libnacl-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY BotDC/ ./BotDC/

WORKDIR /app/BotDC

EXPOSE 8022

CMD ["python", "main.py"]
