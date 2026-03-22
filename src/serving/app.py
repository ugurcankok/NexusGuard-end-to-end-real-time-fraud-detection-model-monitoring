import logging
import uuid
import time
import pandas as pd
from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
from predictor import FraudPredictor
from cassandra.cluster import Cluster
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("NexusGuard-API")

app = FastAPI(title="NexusGuard Real-Time Fraud Detection")

# --- Prometheus Metrics ---
TRANSACTION_COUNT = Counter("total_transactions", "Total number of transactions received")
FRAUD_DETECTED_COUNT = Counter("total_fraud_detected", "Total number of fraud cases detected")
PREDICTION_LATENCY = Histogram("prediction_latency_seconds", "Histogram for model prediction latency")

def get_cassandra_session():
    retries = 10 
    session = None
    while retries > 0:
        try:
            logger.info("Attempting to connect to Cassandra...")
            cluster = Cluster(['nexus_cassandra'], port=9042)
            session = cluster.connect()
            
            # Create Keyspace
            session.execute("""
                CREATE KEYSPACE IF NOT EXISTS nexus_guard 
                WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
            """)
            
            session.set_keyspace('nexus_guard')
            
            # Create the prediction log table
            session.execute("""
                CREATE TABLE IF NOT EXISTS fraud_predictions (
                    transaction_id uuid PRIMARY KEY,
                    transaction_time timestamp,
                    amount double,
                    prediction int,
                    probability float,
                    model_version text
                );
            """)
            
            logger.info("Cassandra connection and schema preparation successful!")
            return session
        except Exception as e:
            logger.warning(f"Waiting for Cassandra... Error: {e} (Retries remaining: {retries})")
            retries -= 1
            time.sleep(15)
            
    logger.error("Failed to connect to Cassandra after multiple attempts!")
    raise Exception("Failed to connect to Cassandra")

# Initialize services
session = get_cassandra_session()
predictor = FraudPredictor()

class Transaction(BaseModel):
    V1: float; V2: float; V3: float; V4: float; V5: float
    V6: float; V7: float; V8: float; V9: float; V10: float
    V11: float; V12: float; V13: float; V14: float; V15: float
    V16: float; V17: float; V18: float; V19: float; V20: float
    V21: float; V22: float; V23: float; V24: float; V25: float
    V26: float; V27: float; V28: float; Amount: float

# Setup Prometheus
Instrumentator().instrument(app).expose(app)

@app.post("/predict")
async def predict_fraud(tx: Transaction):
    TRANSACTION_COUNT.inc()
    start_time = time.time()
    
    try:
        input_df = pd.DataFrame([tx.model_dump()])
        pred, prob = predictor.predict(input_df)
        
        latency = time.time() - start_time
        PREDICTION_LATENCY.observe(latency)
        
        if pred == 1:
            FRAUD_DETECTED_COUNT.inc()
            logger.info(f"Fraud detected! Probability: {prob:.4f}")
        
        tx_id = uuid.uuid4()
        query = """
        INSERT INTO fraud_predictions (transaction_id, transaction_time, amount, prediction, probability, model_version)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        session.execute(query, (tx_id, datetime.now(), tx.Amount, int(pred), prob, "v1"))
        
        return {
            "transaction_id": str(tx_id),
            "is_fraud": bool(pred),
            "probability": prob,
            "status": "Logged to Cassandra"
        }
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        return {"error": "Internal prediction error"}, 500

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)