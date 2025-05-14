FROM python:3.11-slim

WORKDIR /app
COPY data_ingestion.py .

RUN pip install nats-py

CMD ["python", "data_ingestion.py"]
