from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from airflow.utils.dates import days_ago
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from etl.run_etl import run_etl

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'weather_etl_hourly',
    default_args=default_args,
    description='Hourly weather data collection ETL process',
    schedule_interval='@hourly',
    start_date=days_ago(0),
    end_date=datetime.now() + timedelta(days=10),  # Run for next 10 days
    catchup=False,
    tags=['weather', 'etl'],
)

def etl_task():
    """Task to run the ETL process"""
    success = run_etl()
    if not success:
        raise Exception("ETL process failed")

collect_weather = PythonOperator(
    task_id='collect_weather_data',
    python_callable=etl_task,
    dag=dag,
)

# Task dependencies (if we add more tasks in the future)
collect_weather
