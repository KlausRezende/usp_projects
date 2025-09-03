#!/usr/bin/env python3
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

DATA_SOURCE = "/opt/airflow/data_source"
postgres_url = "jdbc:postgresql://postgres_simple:5432/customer_db"
postgres_properties = {"user": "airflow", "password": "airflow", "driver": "org.postgresql.Driver"}

spark = SparkSession.builder.appName("bronze_reclamacoes").config("spark.jars", "/opt/airflow/jars/postgresql-42.6.0.jar").getOrCreate()

def main():
    df = spark.read.option("header", True).option("sep", ";").option("encoding", "ISO-8859-1").csv(f"{DATA_SOURCE}/Reclamacoes/*.csv")
    
    bronze_df = df.select(
        F.col("Ano").cast("integer").alias("ano"),
        F.col("Trimestre").alias("trimestre"),
        F.col("Categoria").alias("categoria"),
        F.col("Tipo").alias("tipo"),
        F.col("CNPJ IF").alias("cnpj_if"),
        F.col("Instituição financeira").alias("instituicao_financeira"),
        F.col("Índice").cast("decimal(10,2)").alias("indice"),
        F.col("Quantidade total de reclamações").cast("integer").alias("total_reclamacoes"),
        df.columns[11]  # Use column index for problematic column
    ).withColumnRenamed(df.columns[11], "total_clientes")
    
    bronze_df.write.jdbc(url=postgres_url, table="tb_bz_reclamacoes", mode="append", properties=postgres_properties)
    print("Bronze reclamacoes data saved")
    
    # Add table comments
    add_table_comments()

def add_table_comments():
    import psycopg2
    try:
        conn = psycopg2.connect(host="postgres_simple", database="customer_db", user="airflow", password="airflow")
        cursor = conn.cursor()
        
        comments = [
            "COMMENT ON TABLE tb_bz_reclamacoes IS 'Tabela bronze com dados brutos de reclamações'",
            "COMMENT ON COLUMN tb_bz_reclamacoes.ano IS 'Ano de referência'",
            "COMMENT ON COLUMN tb_bz_reclamacoes.trimestre IS 'Trimestre de referência'",
            "COMMENT ON COLUMN tb_bz_reclamacoes.categoria IS 'Categoria da instituição'",
            "COMMENT ON COLUMN tb_bz_reclamacoes.tipo IS 'Tipo de instituição'",
            "COMMENT ON COLUMN tb_bz_reclamacoes.cnpj_if IS 'CNPJ da instituição financeira'",
            "COMMENT ON COLUMN tb_bz_reclamacoes.instituicao_financeira IS 'Nome da instituição financeira'",
            "COMMENT ON COLUMN tb_bz_reclamacoes.indice IS 'Índice de reclamações'",
            "COMMENT ON COLUMN tb_bz_reclamacoes.total_reclamacoes IS 'Total de reclamações'",
            "COMMENT ON COLUMN tb_bz_reclamacoes.total_clientes IS 'Total de clientes'"
        ]
        
        for comment in comments:
            cursor.execute(comment)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Table comments added for tb_bz_reclamacoes")
    except Exception as e:
        print(f"❌ Error adding comments: {e}")

if __name__ == "__main__":
    main()
