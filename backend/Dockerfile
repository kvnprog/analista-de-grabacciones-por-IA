FROM python:3.11-slim

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. Instalamos dependencias (están en backend/infrastructure/requirements.txt)
COPY backend/infrastructure/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn uvicorn psycopg2-binary

# 2. Copiamos todo el proyecto
COPY . .

# 3. Configuramos los Paths para que Python encuentre tus carpetas
# /app/backend permite que 'infrastructure' sea visible
# /app/shared permite que 'shared' sea visible
ENV PYTHONPATH=/app/backend:/app/shared

EXPOSE 9100

# 4. El comando de ejecución
# Como el PYTHONPATH incluye /app/backend, Python ya "ve" a infrastructure
CMD ["uvicorn", "infrastructure.fastApiApp:app", "--host", "0.0.0.0", "--port", "9100", "--reload"]