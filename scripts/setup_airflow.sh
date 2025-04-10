#!/bin/bash

# Create Airflow directory structure
mkdir -p ./airflow/dags
mkdir -p ./airflow/logs
mkdir -p ./airflow/plugins

# Set Airflow home
export AIRFLOW_HOME="$(pwd)/airflow"

# Install dependencies
source .venv/bin/activate
pip install -r requirements.txt

# Initialize Airflow database
airflow db init

# Create Airflow user
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin

# Start Airflow webserver (in background)
airflow webserver -p 8080 -D

# Start Airflow scheduler (in background)
airflow scheduler -D

echo "Airflow is now running!"
echo "Access the web interface at http://localhost:8080"
echo "Username: admin"
echo "Password: admin"
echo ""
echo "To stop Airflow, run: pkill -f airflow"
