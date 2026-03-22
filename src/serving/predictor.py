import mlflow.sklearn
import pandas as pd
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("NexusGuard-Predictor")

class FraudPredictor:
    def __init__(self, model_name="NexusGuard_Fraud_Model", stage="None"):
        mlflow.set_tracking_uri("http://mlflow_server:5000")
        
        model_uri = f"models:/{model_name}/{stage}" if stage != "None" else f"models:/{model_name}/latest"
        
        logger.info(f"Attempting to load model from MLflow: {model_uri}")
        
        try:
            self.model = mlflow.sklearn.load_model(model_uri)
            logger.info(f"Model '{model_name}' successfully loaded from {model_uri}")
        except Exception as e:
            logger.error(f"Critical error while loading the model from MLflow: {e}")
            raise

    def predict(self, data: pd.DataFrame):
        try:
            prediction = self.model.predict(data)
            probability = self.model.predict_proba(data)[:, 1]
            
            return prediction[0], float(probability[0])
        except Exception as e:
            logger.error(f"Inference failed during prediction: {e}")
            raise