FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*

COPY requirements_server.txt .
RUN pip install --no-cache-dir -r requirements_server.txt

COPY . .

EXPOSE 8000

CMD ["python", "scripts/server_supervisor.py"]
