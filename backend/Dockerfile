FROM python:3.11-slim

WORKDIR /app

# Install system dependencies needed for compiling packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY tests/ ./tests/

EXPOSE 8000

ENV VECTOR_DB_PATH=/app/data/chroma_db

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
