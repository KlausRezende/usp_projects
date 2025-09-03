import great_expectations as gx
import psycopg2
import pandas as pd
import os

output_path = "/opt/airflow/result/"
output_file = os.path.join(output_path, "validation_results.txt")

os.makedirs(output_path, exist_ok=True)

conn = psycopg2.connect(
    host="postgres_simple",
    database="customer_db",
    user="airflow",
    password="airflow"
)

df = pd.read_sql_query("SELECT * FROM tb_gd_institution_detail", conn)
conn.close()

context = gx.get_context()
datasource = context.sources.add_or_update_pandas(name="pandas_datasource")
data_asset = datasource.add_dataframe_asset(name="institution_detail", dataframe=df)
batch_request = data_asset.build_batch_request()

expectation_name = "institution_detail_dq"
context.add_or_update_expectation_suite(expectation_suite_name=expectation_name)

validator = context.get_validator(
    batch_request=batch_request,
    expectation_suite_name=expectation_name
)

successful_validations = 0

with open(output_file, 'w') as f:

    validator.expect_column_values_to_not_be_null(column="geral")

    validator.expect_column_values_to_be_in_set(column="categoria", value_set=["SUMMARY", "TOP_COMPLAINTS", "EMPLOYEE_METRICS"])

    validator.expect_column_values_to_not_be_null(column="tipo")

    validator.expect_column_values_to_be_between(column="geral", min_value=0.0, max_value=5.0)

    validator.expect_column_values_to_be_between(column="total_reclamacoes", min_value=1, max_value=None)

    results = validator.validate()
    total_validations = len(results['results'])

    for result in results['results']:
        expectation_type = result['expectation_config']['expectation_type']
        column = result['expectation_config']['kwargs'].get('column', 'N/A')
        success = result['success']
        
        if success:
            successful_validations += 1
            
        output = f"Expectativa: {expectation_type} | Coluna: {column} | Sucesso: {success}\n"
        f.write(output)  
        
        if not success:
            failure_details = f"Detalhes da falha: {result}\n"
            f.write(failure_details)
        
        f.write('-' * 60 + '\n')

    success_percentage = (successful_validations / total_validations) * 100

    f.write(f"Percentual de validações bem-sucedidas: {success_percentage:.2f}%\n")
