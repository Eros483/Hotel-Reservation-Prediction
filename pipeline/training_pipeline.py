from src.model_training import ModelTraining
from src.custom_exception import CustomException
from src.data_ingestion import DataIngestion
from src.data_preprocessing import DataProcessor
from config.paths_config import *
from utils.common_functions import *

if __name__=="__main__":
    ### 1. Data ingestion
    config=read_yaml(CONFIG_PATH)
    data_ingestion=DataIngestion(config)
    data_ingestion.run()

    ###2. Data Processing
    processor=DataProcessor(TRAIN_FILE_PATH, TEST_FILE_PATH, PROCESSED_DIR, CONFIG_PATH)
    processor.process()

    ###3. Model Training
    trainer=ModelTraining(PROCESSED_TRAIN_DATA_PATH, PROCESSED_TEST_DATA_PATH, MODEL_OUTPUT_PATH)
    trainer.run()