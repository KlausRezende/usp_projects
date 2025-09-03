#!/usr/bin/env python3
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import types as T

postgres_url = "jdbc:postgresql://postgres_simple:5432/customer_db"
postgres_properties = {"user": "airflow", "password": "airflow", "driver": "org.postgresql.Driver"}

spark = SparkSession.builder.appName("gold_customer").config("spark.jars", "/opt/airflow/jars/postgresql-42.6.0.jar").getOrCreate()

def main():
    # Read from silver tables
    bancos_df = spark.read.jdbc(url=postgres_url, table="tb_sv_bancos", properties=postgres_properties)
    empregados_df = spark.read.jdbc(url=postgres_url, table="tb_sv_empregados", properties=postgres_properties)
    reclamacoes_df = spark.read.jdbc(url=postgres_url, table="tb_sv_reclamacoes", properties=postgres_properties)
    
    # Create meaningful aggregated metrics
    gold_metrics = []
    
    # Metrics by segment from bancos
    bancos_by_segment = bancos_df.groupBy("segmento").agg(
        F.count("*").alias("total_institutions")
    ).collect()
    
    for row in bancos_by_segment:
        gold_metrics.append((
            f"Segmento {row.segmento}",  # nome
            "SUMMARY",  # categoria
            "SEGMENT_METRICS",  # tipo
            f"Total: {row.total_institutions}",  # indice
            None,  # geral
            None   # total_reclamacoes
        ))
    
    # Top institutions by complaints
    top_complaints = reclamacoes_df.groupBy("instituicao_financeira").agg(
        F.sum("total_reclamacoes").alias("sum_reclamacoes")
    ).orderBy(F.desc("sum_reclamacoes")).limit(5).collect()
    
    for row in top_complaints:
        gold_metrics.append((
            row.instituicao_financeira,  # nome
            "TOP_COMPLAINTS",  # categoria
            "RANKING",  # tipo
            "Rank: Top 5",  # indice
            None,  # geral
            int(row.sum_reclamacoes) if row.sum_reclamacoes else 0  # total_reclamacoes
        ))
    
    # Employee satisfaction metrics
    emp_metrics = empregados_df.agg(
        F.avg("avg_geral").alias("avg_satisfaction"),
        F.count("*").alias("total_companies")
    ).collect()[0]
    
    gold_metrics.append((
        "Employee Satisfaction Summary",  # nome
        "EMPLOYEE_METRICS",  # categoria
        "SATISFACTION",  # tipo
        f"Companies: {emp_metrics.total_companies}",  # indice
        float(emp_metrics.avg_satisfaction) if emp_metrics.avg_satisfaction else 0.0,  # geral
        None   # total_reclamacoes
    ))
    
    # Create DataFrame with metrics
    schema = T.StructType([
        T.StructField("nome", T.StringType(), True),
        T.StructField("categoria", T.StringType(), True),
        T.StructField("tipo", T.StringType(), True),
        T.StructField("indice", T.StringType(), True),
        T.StructField("geral", T.DoubleType(), True),
        T.StructField("total_reclamacoes", T.IntegerType(), True)
    ])
    
    final_df = spark.createDataFrame(gold_metrics, schema)
    
    final_df.write.jdbc(url=postgres_url, table="tb_gd_institution_detail", mode="overwrite", properties=postgres_properties)
    print("Gold institution detail data saved with simplified structure")
    
    # Add table comments
    add_table_comments()

def add_table_comments():
    import psycopg2
    try:
        conn = psycopg2.connect(host="postgres_simple", database="customer_db", user="airflow", password="airflow")
        cursor = conn.cursor()
        
        comments = [
            "COMMENT ON TABLE tb_gd_institution_detail IS 'Tabela gold com métricas agregadas de instituições'",
            "COMMENT ON COLUMN tb_gd_institution_detail.nome IS 'Nome da instituição ou métrica'",
            "COMMENT ON COLUMN tb_gd_institution_detail.categoria IS 'Categoria da métrica'",
            "COMMENT ON COLUMN tb_gd_institution_detail.tipo IS 'Tipo de análise'",
            "COMMENT ON COLUMN tb_gd_institution_detail.indice IS 'Índice ou descrição da métrica'",
            "COMMENT ON COLUMN tb_gd_institution_detail.geral IS 'Valor geral da métrica'",
            "COMMENT ON COLUMN tb_gd_institution_detail.total_reclamacoes IS 'Total de reclamações'"
        ]
        
        for comment in comments:
            cursor.execute(comment)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Table comments added for tb_gd_institution_detail")
    except Exception as e:
        print(f"❌ Error adding comments: {e}")

if __name__ == "__main__":
    main()
