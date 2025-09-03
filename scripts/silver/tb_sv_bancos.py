#!/usr/bin/env python3
from pyspark.sql import SparkSession

postgres_url = "jdbc:postgresql://postgres_simple:5432/customer_db"
postgres_properties = {"user": "airflow", "password": "airflow", "driver": "org.postgresql.Driver"}

spark = SparkSession.builder.appName("silver_bancos").config("spark.jars", "/opt/airflow/jars/postgresql-42.6.0.jar").getOrCreate()

def main():
    bronze_df = spark.read.jdbc(url=postgres_url, table="tb_bz_bancos", properties=postgres_properties)
    
    # Clean and transform data
    silver_df = bronze_df.filter(bronze_df.cnpj.isNotNull() & bronze_df.nome.isNotNull())
    
    silver_df.write.jdbc(url=postgres_url, table="tb_sv_bancos", mode="overwrite", properties=postgres_properties)
    print("Silver bancos data saved")
    
    # Add table comments
    add_table_comments()

def add_table_comments():
    import psycopg2
    try:
        conn = psycopg2.connect(host="postgres_simple", database="customer_db", user="airflow", password="airflow")
        cursor = conn.cursor()
        
        comments = [
            "COMMENT ON TABLE tb_sv_bancos IS 'Tabela silver com dados limpos de bancos'",
            "COMMENT ON COLUMN tb_sv_bancos.segmento IS 'Segmento do banco'",
            "COMMENT ON COLUMN tb_sv_bancos.cnpj IS 'CNPJ da instituição'",
            "COMMENT ON COLUMN tb_sv_bancos.nome IS 'Nome da instituição'"
        ]
        
        for comment in comments:
            cursor.execute(comment)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Table comments added for tb_sv_bancos")
    except Exception as e:
        print(f"❌ Error adding comments: {e}")

if __name__ == "__main__":
    main()
