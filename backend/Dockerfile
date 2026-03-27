FROM python:3.11-slim

WORKDIR /app

COPY infrastructure/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y ffmpeg
COPY . .

EXPOSE 9100

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "infrastructure.fastApiApp:app", "--bind", "0.0.0.0:9100"]

