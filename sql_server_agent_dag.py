from airflow import DAG
from airflow.providers.microsoft.mssql.operators.mssql import MsSqlOperator
from airflow.providers.microsoft.mssql.sensors.mssql import MsSqlSensor
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 6, 26),
    'email': ['your@email.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'sql_server_agent_dag',
    default_args=default_args,
    description='Execute SQL Server Agent jobs with Airflow',
    schedule_interval='@daily',
)

# Define the SQL Server connection details as Airflow connection variables.

job_name = 'YourAgentJobName'

t1 = MsSqlOperator(
    task_id='step_1',
    mssql_conn_id='your_sql_server_conn',
    sql='EXEC msdb.dbo.sp_start_job @job_name = %s',
    params=[job_name],
    dag=dag,
)

t2 = MsSqlSensor(
    task_id='step_2',
    mssql_conn_id='your_sql_server_conn',
    sql=f"SELECT current_execution_status FROM msdb.dbo.sysjobactivity WHERE job_id IN (SELECT job_id FROM msdb.dbo.sysjobs WHERE name = '{job_name}')",
    mode='poke',
    poke_interval=60,  # Check every 60 seconds
    timeout=600,  # Timeout after 600 seconds (10 minutes)
    dag=dag,
)

t3 = MsSqlOperator(
    task_id='step_3',
    mssql_conn_id='your_sql_server_conn',
    sql='EXEC your_stored_procedure',
    dag=dag,
)

t1 >> t2 >> t3
