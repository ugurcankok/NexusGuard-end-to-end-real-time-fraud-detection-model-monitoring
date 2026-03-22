import os
import mlflow
import mlflow.sklearn
import logging
from sklearn.metrics import f1_score, precision_score, recall_score
from data_loader import FraudDataLoader
from model import FraudModel

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("NexusGuard-Trainer")

# MLflow Setup
TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow_server:5000")
mlflow.set_tracking_uri(TRACKING_URI)

def run_experiment(n_estimators, max_depth):
    experiment_name = "NexusGuard_Fraud_Detection"
    mlflow.set_experiment(experiment_name)
    
    logger.info(f"MLflow Tracking URI initialized at: {mlflow.get_tracking_uri()}")

    try:
        loader = FraudDataLoader()
        loader.load_data()
        X_train, X_test, y_train, y_test = loader.prepare_data()
        logger.info("Dataset successfully loaded and split into train/test sets.")
    except Exception as e:
        logger.error(f"Failed to prepare data: {e}")
        raise

    run_name = f"RF_E{n_estimators}_D{max_depth}"
    with mlflow.start_run(run_name=run_name) as run:
        logger.info(f"Starting MLflow run: {run_name}")

        fraud_model = FraudModel(n_estimators=n_estimators, max_depth=max_depth)
        logger.info(f"Training Random Forest with n_estimators={n_estimators}, max_depth={max_depth}...")
        fraud_model.train(X_train, y_train)
        
        predictions = fraud_model.predict(X_test)
        f1 = f1_score(y_test, predictions)
        precision = precision_score(y_test, predictions)
        recall = recall_score(y_test, predictions)

        # Logging Parameters and Metrics to MLflow
        mlflow.log_params({"n_estimators": n_estimators, "max_depth": max_depth})
        mlflow.log_metrics({
            "f1_score": f1,
            "precision": precision,
            "recall": recall
        })
        logger.info(f"Metrics Logged - F1: {f1:.4f} | Precision: {precision:.4f} | Recall: {recall:.4f}")

        # Artifact Management & Model Registry
        try:
            mlflow.sklearn.log_model(
                sk_model=fraud_model.model,
                artifact_path="model"
            )
            
            run_id = run.info.run_id
            model_uri = f"runs:/{run_id}/model"
            
            logger.info(f"Registering model version for run: {run_id}")
            mlflow.register_model(model_uri, "NexusGuard_Fraud_Model")
            
            logger.info(f"Experiment Finished Successfully! Run ID: {run_id}")
        except Exception as e:
            logger.error(f"Error during model logging/registration: {e}")
            raise

if __name__ == "__main__":
    run_experiment(n_estimators=100, max_depth=10)