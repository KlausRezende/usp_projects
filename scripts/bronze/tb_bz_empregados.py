#!/usr/bin/env python3
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

DATA_SOURCE = "/opt/airflow/data_source"
postgres_url = "jdbc:postgresql://postgres_simple:5432/customer_db"
postgres_properties = {"user": "airflow", "password": "airflow", "driver": "org.postgresql.Driver"}

spark = SparkSession.builder.appName("bronze_empregados").config("spark.jars", "/opt/airflow/jars/postgresql-42.6.0.jar").getOrCreate()

def main():
    df = spark.read.option("header", True).option("sep", "|").csv(f"{DATA_SOURCE}/Empregados/*.csv")
    
    bronze_df = df.select(
        F.col("Segmento").alias("segmento"),
        F.col("Nome").alias("nome"),
        F.col("Geral").cast("decimal(3,2)").alias("geral"),
        F.col("Cultura e valores").cast("decimal(3,2)").alias("cultura_valores"),
        F.col("Diversidade e inclusão").cast("decimal(3,2)").alias("diversidade_inclusao"),
        F.col("Qualidade de vida").cast("decimal(3,2)").alias("qualidade_vida"),
        F.col("Alta liderança").cast("decimal(3,2)").alias("alta_lideranca"),
        F.col("Remuneração e benefícios").cast("decimal(3,2)").alias("remuneracao_beneficios"),
        F.col("Oportunidades de carreira").cast("decimal(3,2)").alias("oportunidades_carreira"),
        F.col("match_percent").cast("integer").alias("match_percent")
    )
    
    bronze_df.write.jdbc(url=postgres_url, table="tb_bz_empregados", mode="append", properties=postgres_properties)
    print("Bronze empregados data saved")
    
    # Add table comments
    add_table_comments()

def add_table_comments():
    import psycopg2
    try:
        conn = psycopg2.connect(host="postgres_simple", database="customer_db", user="airflow", password="airflow")
        cursor = conn.cursor()
        
        comments = [
            "COMMENT ON TABLE tb_bz_empregados IS 'Tabela bronze com dados brutos de empregados'",
            "COMMENT ON COLUMN tb_bz_empregados.segmento IS 'Segmento da empresa'",
            "COMMENT ON COLUMN tb_bz_empregados.nome IS 'Nome da empresa'",
            "COMMENT ON COLUMN tb_bz_empregados.geral IS 'Nota geral'",
            "COMMENT ON COLUMN tb_bz_empregados.cultura_valores IS 'Nota cultura e valores'",
            "COMMENT ON COLUMN tb_bz_empregados.diversidade_inclusao IS 'Nota diversidade e inclusão'",
            "COMMENT ON COLUMN tb_bz_empregados.qualidade_vida IS 'Nota qualidade de vida'",
            "COMMENT ON COLUMN tb_bz_empregados.alta_lideranca IS 'Nota alta liderança'",
            "COMMENT ON COLUMN tb_bz_empregados.remuneracao_beneficios IS 'Nota remuneração e benefícios'",
            "COMMENT ON COLUMN tb_bz_empregados.oportunidades_carreira IS 'Nota oportunidades de carreira'",
            "COMMENT ON COLUMN tb_bz_empregados.match_percent IS 'Percentual de match'"
        ]
        
        for comment in comments:
            cursor.execute(comment)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Table comments added for tb_bz_empregados")
    except Exception as e:
        print(f"❌ Error adding comments: {e}")

if __name__ == "__main__":
    main()
