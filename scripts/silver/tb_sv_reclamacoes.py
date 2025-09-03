#!/usr/bin/env python3
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

postgres_url = "jdbc:postgresql://postgres_simple:5432/customer_db"
postgres_properties = {"user": "airflow", "password": "airflow", "driver": "org.postgresql.Driver"}

spark = SparkSession.builder.appName("silver_reclamacoes").config("spark.jars", "/opt/airflow/jars/postgresql-42.6.0.jar").getOrCreate()

def main():
    bronze_df = spark.read.jdbc(url=postgres_url, table="tb_bz_reclamacoes", properties=postgres_properties)
    
    # Aggregate by year, quarter and institution
    silver_df = bronze_df.groupBy("ano", "trimestre", "cnpj_if", "instituicao_financeira").agg(
        F.sum("total_reclamacoes").alias("total_reclamacoes"),
        F.sum("total_clientes").alias("total_clientes")
    )
    
    silver_df.write.jdbc(url=postgres_url, table="tb_sv_reclamacoes", mode="overwrite", properties=postgres_properties)
    print("Silver reclamacoes data saved")
    
    # Add table comments
    add_table_comments()

def add_table_comments():
    import psycopg2
    try:
        conn = psycopg2.connect(host="postgres_simple", database="customer_db", user="airflow", password="airflow")
        cursor = conn.cursor()
        
        comments = [
            "COMMENT ON TABLE tb_sv_reclamacoes IS 'Tabela silver com dados limpos de reclamações'",
            "COMMENT ON COLUMN tb_sv_reclamacoes.ano IS 'Ano de referência'",
            "COMMENT ON COLUMN tb_sv_reclamacoes.trimestre IS 'Trimestre de referência'",
            "COMMENT ON COLUMN tb_sv_reclamacoes.cnpj_if IS 'CNPJ da instituição financeira'",
            "COMMENT ON COLUMN tb_sv_reclamacoes.instituicao_financeira IS 'Nome da instituição financeira'",
            "COMMENT ON COLUMN tb_sv_reclamacoes.total_reclamacoes IS 'Total de reclamações'",
            "COMMENT ON COLUMN tb_sv_reclamacoes.total_clientes IS 'Total de clientes'"
        ]
        
        for comment in comments:
            cursor.execute(comment)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Table comments added for tb_sv_reclamacoes")
    except Exception as e:
        print(f"❌ Error adding comments: {e}")

if __name__ == "__main__":
    main()
