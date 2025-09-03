FROM python:3.9

RUN apt-get update -yqq && \
    apt-get install -yqq default-jdk && \
    apt-get clean

# Airflow setup
ENV AIRFLOW_HOME=/opt/airflow
ENV AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
ENV PYTHONPATH=/opt/airflow
ENV AIRFLOW__CORE__EXECUTOR=LocalExecutor

# Create jars directory and copy PostgreSQL JDBC driver
RUN mkdir -p /opt/airflow/jars
COPY jars/postgresql-42.6.0.jar /opt/airflow/jars/

#COPY ./dags $AIRFLOW_HOME/dags/
COPY requirements.txt ./
RUN pip3 install --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt


COPY start.sh /opt/airflowinit/start.sh
RUN chmod +x /opt/airflowinit/start.sh
RUN sed -i 's/\r$//' /opt/airflowinit/start.sh
EXPOSE 8080


RUN apt-get update && apt-get install -y supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
CMD ["/usr/bin/supervisord"]