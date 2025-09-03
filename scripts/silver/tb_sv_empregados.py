#!/usr/bin/env python3
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

postgres_url = "jdbc:postgresql://postgres_simple:5432/customer_db"
postgres_properties = {"user": "airflow", "password": "airflow", "driver": "org.postgresql.Driver"}

spark = SparkSession.builder.appName("silver_empregados").config("spark.jars", "/opt/airflow/jars/postgresql-42.6.0.jar").getOrCreate()

def main():
    bronze_df = spark.read.jdbc(url=postgres_url, table="tb_bz_empregados", properties=postgres_properties)
    
    # Aggregate by segmento and nome
    silver_df = bronze_df.groupBy("segmento", "nome").agg(
        F.avg("geral").alias("avg_geral"),
        F.avg("cultura_valores").alias("avg_cultura_valores")
    )
    
    silver_df.write.jdbc(url=postgres_url, table="tb_sv_empregados", mode="overwrite", properties=postgres_properties)
    print("Silver empregados data saved")
    
    # Add table comments
    add_table_comments()

def add_table_comments():
    import psycopg2
    try:
        conn = psycopg2.connect(host="postgres_simple", database="customer_db", user="airflow", password="airflow")
        cursor = conn.cursor()
        
        comments = [
            "COMMENT ON TABLE tb_sv_empregados IS 'Tabela silver com dados limpos de empregados'",
            "COMMENT ON COLUMN tb_sv_empregados.segmento IS 'Segmento da empresa'",
            "COMMENT ON COLUMN tb_sv_empregados.nome IS 'Nome da empresa'",
            "COMMENT ON COLUMN tb_sv_empregados.avg_geral IS 'Média da nota geral'",
            "COMMENT ON COLUMN tb_sv_empregados.avg_cultura_valores IS 'Média da nota cultura e valores'"
        ]
        
        for comment in comments:
            cursor.execute(comment)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Table comments added for tb_sv_empregados")
    except Exception as e:
        print(f"❌ Error adding comments: {e}")

if __name__ == "__main__":
    main()
