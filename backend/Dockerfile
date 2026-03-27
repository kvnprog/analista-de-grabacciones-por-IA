FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY infrastructure/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 9100

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "infrastructure.fastApiApp:app", "--bind", "0.0.0.0:9100", "--timeout", "300"]

