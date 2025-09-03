# USP Projects

## Login Credentials

### Airflow
- **Username:** admin
- **Password:** admin

### OpenMetadata
- **Username:** admin@open-metadata.org
- **Password:** adminpostgres_simple

## OpenMetadata Database Configuration

### Como configurar a conexão PostgreSQL no OpenMetadata:

1. **Faça login no OpenMetadata** (linha 9 acima)
2. **Dentro do OpenMetadata**, configure a conexão PostgreSQL com os seguintes dados:
   - **Username:** airflow
   - **Auth Configuration Type:** Basic Auth
   - **Password:** airflow
   - **Host and Port:** postgres_simple:5432
   - **Database:** customer_db
   - **Configuration:** Ingest All Databases