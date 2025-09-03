import yaml
from datetime import datetime, timedelta
from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

from libs.log import log_callback_success
from libs.log import log_callback_fail
from libs.log import notification_discord


with open(f'/opt/airflow/dags/parameters_institution_detail.yaml','r') as f:
   parameters = yaml.safe_load(f)

default_args = {
    'owner': 'Klaus_Rezende'
}

with DAG(
    dag_id=f"{parameters['config']['dag_name']}",
    start_date=datetime(2023, 12, 31), 
    schedule_interval= parameters['config']['schedule_interval'],
    catchup=False,
    default_args=default_args,
    on_success_callback=log_callback_success,
    on_failure_callback=log_callback_fail
) as dag:

    start = EmptyOperator(
        task_id='start_pipeline',
        dag=dag
    )

    tasks = {}

    # Create bronze tasks
    bronze_tasks = []
    for script in parameters['run_scripts']['bronze']['scripts']:
        task = BashOperator(
            task_id=script['name'],
            bash_command=script['command']
        )
        tasks[script['name']] = task
        bronze_tasks.append(task)

    # Create silver tasks
    silver_tasks = []
    for script in parameters['run_scripts']['silver']['scripts']:
        task = BashOperator(
            task_id=script['name'],
            bash_command=script['command']
        )
        tasks[script['name']] = task
        silver_tasks.append(task)

    # Create gold tasks
    gold_tasks = []
    for script in parameters['run_scripts']['gold']['scripts']:
        task = BashOperator(
            task_id=script['name'],
            bash_command=script['command']
        )
        tasks[script['name']] = task
        gold_tasks.append(task)

    # Create trigger task
    trigger_task = TriggerDagRunOperator(
        task_id='trigger_dataquality',
        trigger_dag_id=parameters['triggers'][0]['dag_id']
    )

    end = EmptyOperator(
        task_id='finish_pipeline',
        dag=dag
    )

    # Set dependencies
    start >> bronze_tasks

    # Silver dependencies
    for script in parameters['run_scripts']['silver']['scripts']:
        tasks[script['name']].set_upstream(tasks[script['depends_on']])

    # Gold dependencies
    for script in parameters['run_scripts']['gold']['scripts']:
        for dep in script['depends_on']:
            tasks[script['name']].set_upstream(tasks[dep])

    # Final dependencies
    gold_tasks >> trigger_task >> end
