import os
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import RandomizedSearchCV
import lightgbm as lgb
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *
from config.model_params import *
from utils.common_functions import read_yaml, load_data
from scipy.stats import randint
import mlflow
import mlflow.sklearn


logger=get_logger(__name__)

class ModelTraining:
    def __init__(self, train_path, test_path, model_output_path):
        self.train_path=train_path
        self.test_path=test_path
        self.model_output_path=model_output_path

        self.params_dist=LIGHTGM_PARAMS
        self.random_search_params=RANDOM_SEARCH_PARAMS

    def load_and_split_data(self):
        try:
            logger.info(f"Loading data from {self.train_path} and {self.test_path}")
            train_df=load_data(self.train_path)
            test_df=load_data(self.test_path)

            logger.info(f"Splitting Data")
            X_train=train_df.drop(columns=["booking_status"])
            y_train=train_df["booking_status"]

            X_test=test_df.drop(columns=["booking_status"])
            y_test=test_df["booking_status"]

            logger.info("Data split succesful for model training utilisation")
            return X_train, y_train, X_test, y_test
        
        except Exception as e:
            logger.error(f"Error occurred while loading and splitting data: {str(e)}")
            raise CustomException(f"Error occurred while loading and splitting data: {str(e)}", e)
        
    def train_lgbm(self, X_train, y_train):
        try:
            logger.info("Training LightGBM model")
            
            lgbm_model=lgb.LGBMClassifier(random_state=self.random_search_params["random_state"])
            logger.info("Starting hyperparameter tuning")

            random_search=RandomizedSearchCV(
                estimator=lgbm_model,
                param_distributions=self.params_dist,
                n_iter=self.random_search_params["n_iter"],
                cv=self.random_search_params["cv"],
                n_jobs=self.random_search_params["n_jobs"],
                random_state=self.random_search_params["random_state"],
                verbose=self.random_search_params["verbose"],
                scoring=self.random_search_params["scoring"],
            )

            logger.info("Starting hyper parameter tuning")

            random_search.fit(X_train, y_train)
            logger.info("Hyper parameter tuning completed")

            best_params=random_search.best_params_

            best_lgbm_model=random_search.best_estimator_

            logger.info(f"Best parameters are: {best_params}")

            return best_lgbm_model
        
        except Exception as e:
            logger.error(f"Error occurred while training LightGBM model: {str(e)}")
            raise CustomException(f"Error occurred while training LightGBM model", e)
        
    def evaluate_model(self, model, X_test, y_test):
        try:
            y_pred=model.predict(X_test)

            accuracy=accuracy_score(y_test, y_pred)
            precision=precision_score(y_test, y_pred)
            recall=recall_score(y_test, y_pred)
            f1=f1_score(y_test, y_pred)

            logger.info(f"Accuracy Score: {accuracy}")
            logger.info(f"Precision Score: {precision}")
            logger.info(f"Recall Score: {recall}")
            logger.info(f"F1 Score: {f1}")

            return {
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1": f1
            }

        except Exception as e:
            logger.error(f"Error occurred while evaluating model: {str(e)}")
            raise CustomException(f"Error occurred while evaluating model", e)
        
    def save_model(self, model):
        try:
            os.makedirs(os.path.dirname(self.model_output_path), exist_ok=True)
            
            logger.info("Saving model")
            joblib.dump(model, self.model_output_path)
            logger.info(f"Saved model to {self.model_output_path}")

        except Exception as e:
            logger.error(f"Error occurred while saving model: {str(e)}")
            raise CustomException(f"Error occurred while saving model", e)
        
    def run(self):
        try:
            with mlflow.start_run():
                logger.info("Initialising model training pipeline, and started MLFlow experimentation.")

                logger.info("Logging training and testing dataset to MLFlow")

                mlflow.log_artifact(self.train_path, artifact_path="datasets")
                mlflow.log_artifact(self.test_path, artifact_path="datasets")

                X_train, y_train, X_test, y_test=self.load_and_split_data()
                best_lgbm_model=self.train_lgbm(X_train, y_train)
                metrics=self.evaluate_model(best_lgbm_model, X_test, y_test)
                self.save_model(best_lgbm_model)

                logger.info("Logging model, metrics and parameters in mlflow")
                mlflow.log_artifact(self.model_output_path)
                mlflow.log_metrics(metrics)
                mlflow.log_params(best_lgbm_model.get_params())

                logger.info("Model training completed.")

        except Exception as e:
            logger.error(f"Error occurred while running model training pipeline: {str(e)}")
            raise CustomException(f"Error occurred while running model training pipeline", e)
        

if __name__=="__main__":
    trainer=ModelTraining(PROCESSED_TRAIN_DATA_PATH, PROCESSED_TEST_DATA_PATH, MODEL_OUTPUT_PATH)
    trainer.run()