from datetime import datetime
from discord_webhook import DiscordWebhook
import pytz

utc_now = datetime.now(pytz.utc)
sp_timezone = pytz.timezone('America/Sao_Paulo')
sp_now = utc_now.astimezone(sp_timezone)
formatted_sp_now = sp_now.strftime("%y-%m-%d %H:%M:%S")


def notification_discord(message):
    webhook = DiscordWebhook(url="https://discord.com/api/webhooks/1296310245202726982/uDk_zhb4Y9n5F5xS9y6W8EsFTcDhlbqRl080pt6WOd-u4-aCBjh_9vouZRByPzxB4HkY", content= f"{message}")
    response = webhook.execute()


def log_callback_fail(context):
    ti = context['task_instance']
    dag_run = context.get('dag_run')
    task_instances = dag_run.get_task_instances()
    dag_state = 'failed'
    dag_id = dag_run.dag_id
    start_date = dag_run.start_date
    end_date = dag_run.end_date
    duration = (dag_run.end_date - dag_run.start_date).total_seconds()
    message = f"Alerting the Discord of the Data Engineering team, the DAG: {dag_id} has issues.  {formatted_sp_now}"
    notification_discord(message)
    

def log_callback_success(context):
    dag_run = context.get('dag_run')
    task_instances = dag_run.get_task_instances()
    dag_state = 'success'
    dag_id = dag_run.dag_id
    start_date = dag_run.start_date
    end_date = dag_run.end_date
    duration = (dag_run.end_date - dag_run.start_date).total_seconds()
