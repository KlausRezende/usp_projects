import yaml
from datetime import datetime, timedelta
from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.operators.python import BranchPythonOperator

from libs.log import log_callback_success
from libs.log import log_callback_fail
from libs.log import notification_discord

with open(f'/opt/airflow/dags/parameters_institution_detail_data_quality.yaml','r') as f:
   parameters = yaml.safe_load(f)

default_args = {
    'owner': 'Klaus_Rezende'
}

def validate_percentage():
    """Validate data quality percentage"""
    with open('/opt/airflow/result/validation_results.txt', 'r') as file:
        lines = file.readlines()  
        last_line = lines[-1].strip() 

    if "Percentual de validações bem-sucedidas:" in last_line:
        percentage_str = last_line.split(":")[1].strip().replace('%', '')
        percentage = float(percentage_str)

        print(f"📊 Data Quality Results: {percentage}%")
        
        if percentage > parameters['config']['data_quality_percentage']:
            return 'valid'
        else:
            return 'invalid'

def error():
    message = "❌ Data Quality validation failed - notifying team"
    notification_discord(message)
    raise Exception("Data Quality validation failed...")

with DAG(
    dag_id=f"{parameters['config']['dag_name']}",
    start_date=datetime(2023, 12, 31),
    schedule_interval=parameters['config']['schedule_interval'],
    catchup=False,
    default_args=default_args,
    on_success_callback=log_callback_success,
    on_failure_callback=log_callback_fail
) as dag:

    start = EmptyOperator(
        task_id='start_pipeline',
        dag=dag
    )

    run_data_quality = BashOperator(
        task_id='run_data_quality',
        bash_command='python3 /opt/airflow/scripts/data_quality/data_quality_institution.py'
    )

    validate_logs = BranchPythonOperator(
        task_id="validate",
        python_callable=validate_percentage
    )

    valid = BashOperator(
        task_id="valid",
        bash_command="echo '✅ Data Quality validation passed'"
    )

    invalid = PythonOperator(
        task_id="invalid",
        python_callable=error
    )

    start >> run_data_quality >> validate_logs >> [valid, invalid]
