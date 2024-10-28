from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import pandas as pd
import os
from kaggle.api.kaggle_api_extended import KaggleApi
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Define default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
}

# Initialize the DAG
dag = DAG(
    'bangalore_house_price_dag',
    default_args=default_args,
    description='A DAG to process Bangalore house price dataset',
    schedule_interval='@daily',
    start_date=days_ago(1),
    catchup=False,
)

# Define paths
project_dir = ''
raw_data_dir = os.path.join(project_dir, 'data/raw')
processed_data_dir = os.path.join(project_dir, 'data/processed')
raw_data_path = os.path.join(raw_data_dir, 'Bengaluru_House_Data.csv')
processed_data_path = os.path.join(processed_data_dir, 'cleaned_bangalore_house_prices.csv')

# Task 1: Download dataset from Kaggle
def download_dataset():
    kaggle_username = os.getenv('KAGGLE_USERNAME')
    kaggle_key = os.getenv('KAGGLE_KEY')
    
    if not kaggle_username or not kaggle_key:
        raise ValueError("Kaggle credentials are not set in environment variables")
    
    api = KaggleApi()
    api.authenticate()
    
    # Ensure directories exist
    os.makedirs(raw_data_dir, exist_ok=True)
    
    api.dataset_download_files(
        'amitabhajoy/bengaluru-house-price-data',
        path=raw_data_dir,
        unzip=True
    )
    print("Dataset downloaded to:", raw_data_dir)
    
    df = pd.read_csv(raw_data_path)
    print("First few rows of the downloaded dataset:")
    print(df.head())

# Task 2: Process the dataset
def process_dataset():
    # Ensure directories exist
    os.makedirs(processed_data_dir, exist_ok=True)
    
    # Load the dataset
    df = pd.read_csv(raw_data_path)
    
    # Drop unnecessary columns
    columns_to_drop = ['area_type', 'society', 'balcony', 'availability']
    df.drop(columns=columns_to_drop, inplace=True)
    
    # Handle missing values
    df.dropna(inplace=True)
    
    # Save the processed dataset
    df.to_csv(processed_data_path, index=False)

# Define the tasks
download_task = PythonOperator(
    task_id='download_dataset',
    python_callable=download_dataset,
    dag=dag,
)

process_task = PythonOperator(
    task_id='process_dataset',
    python_callable=process_dataset,
    dag=dag,
)

# Set task dependencies
download_task >> process_task
