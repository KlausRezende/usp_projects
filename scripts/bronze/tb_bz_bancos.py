#!/usr/bin/env python3
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

DATA_SOURCE = "/opt/airflow/data_source"
postgres_url = "jdbc:postgresql://postgres_simple:5432/customer_db"
postgres_properties = {"user": "airflow", "password": "airflow", "driver": "org.postgresql.Driver"}

spark = SparkSession.builder.appName("bronze_bancos").config("spark.jars", "/opt/airflow/jars/postgresql-42.6.0.jar").getOrCreate()

def main():
    df = spark.read.option("header", True).option("sep", "\t").csv(f"{DATA_SOURCE}/Bancos/*.tsv")
    
    bronze_df = df.select(
        F.col("Segmento").alias("segmento"),
        F.col("CNPJ").alias("cnpj"),
        F.col("Nome").alias("nome")
    )
    
    bronze_df.write.jdbc(url=postgres_url, table="tb_bz_bancos", mode="append", properties=postgres_properties)
    print("Bronze bancos data saved")
    
    # Add table comments
    add_table_comments()

def add_table_comments():
    import psycopg2
    try:
        conn = psycopg2.connect(host="postgres_simple", database="customer_db", user="airflow", password="airflow")
        cursor = conn.cursor()
        
        comments = [
            "COMMENT ON TABLE tb_bz_bancos IS 'Tabela bronze com dados brutos de bancos'",
            "COMMENT ON COLUMN tb_bz_bancos.segmento IS 'Segmento do banco'",
            "COMMENT ON COLUMN tb_bz_bancos.cnpj IS 'CNPJ da instituição'",
            "COMMENT ON COLUMN tb_bz_bancos.nome IS 'Nome da instituição'"
        ]
        
        for comment in comments:
            cursor.execute(comment)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Table comments added for tb_bz_bancos")
    except Exception as e:
        print(f"❌ Error adding comments: {e}")

if __name__ == "__main__":
    main()
