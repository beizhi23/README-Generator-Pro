FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

COPY readme-generator-pro/assets/readme-generator-pro/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY readme-generator-pro/assets/readme-generator-pro .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
