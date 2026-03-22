import json
import requests
import logging
from kafka import KafkaConsumer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("NexusGuard-Consumer")

# Kafka and API Configurations
KAFKA_TOPIC = "fraud_transactions"
KAFKA_SERVER = "nexus_kafka:29092"
API_URL = "http://nexus_serving:8000/predict"

try:
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=[KAFKA_SERVER],
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        group_id="fraud_detection_group"
    )

    logger.info(f"Connected to Kafka topic: {KAFKA_TOPIC} at {KAFKA_SERVER}")
except Exception as e:
    logger.error(f"Failed to initialize Kafka Consumer: {e}")
    raise

logger.info("Consumer is listening for incoming transactions...")

for message in consumer:
    tx_data = message.value
    
    try:
        response = requests.post(API_URL, json=tx_data)
        response.raise_for_status()
        
        result = response.json()
        
        logger.info(
            f"Transaction Processed - ID: {result.get('transaction_id')} | "
            f"Is Fraud: {result.get('is_fraud')} | "
            f"Probability: {result.get('probability'):.4f}"
        )
        
    except requests.exceptions.RequestException as e:
        logger.error(f"API Connection Error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error while processing transaction: {e}")