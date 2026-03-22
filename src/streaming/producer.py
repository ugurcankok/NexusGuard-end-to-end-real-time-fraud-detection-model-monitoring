import pandas as pd
from kafka import KafkaProducer
import json
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("NexusGuard-Producer")

# Kafka Settings
KAFKA_TOPIC = "fraud_transactions"
KAFKA_SERVER = "nexus_kafka:29092" 

try:
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_SERVER],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    logger.info(f"Successfully connected to Kafka at {KAFKA_SERVER}")
except Exception as e:
    logger.error(f"Failed to connect to Kafka: {e}")
    raise

def stream_data(file_path):
    try:
        df = pd.read_csv(file_path)
        logger.info(f"Loaded dataset from {file_path}. Total transactions: {len(df)}")
        logger.info(f"Starting data stream to Kafka topic: {KAFKA_TOPIC}...")
        
        for index, row in df.iterrows():
            data = row.to_dict()
            producer.send(KAFKA_TOPIC, value=data)

            if index % 10 == 0:
                logger.info(f"Progress: {index} transactions successfully streamed.")
                
            time.sleep(0.5)
            
    except FileNotFoundError:
        logger.error(f"Dataset file not found at: {file_path}")
    except Exception as e:
        logger.error(f"Error during data streaming: {e}")

if __name__ == "__main__":
    DATA_PATH = "data/creditcard.csv"
    stream_data(DATA_PATH)