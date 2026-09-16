FROM python:3.10-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN pip install --no-cache-dir "mcp==2.2.0" "uvicorn>=0.34.0"

COPY server.py /app/server.py

EXPOSE 8000

CMD ["python", "server.py"]
