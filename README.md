# USP Projects

## Pré-requisitos

- Docker
- Docker Compose

## Guia de Instalação

### 1. Clone o repositório
```bash
git clone https://github.com/KlausRezende/usp_projects.git
```

### 2. Navegue para o diretório
```bash
cd usp_projects
```

### 3. Execute o pipeline
```bash
./start_pipeline.sh
```

### 4. Acesse as aplicações
Após a execução, acesse as URLs disponibilizadas e faça login com as credenciais abaixo.

## Credenciais de Acesso

### Airflow
- **Usuário:** admin
- **Senha:** admin

### OpenMetadata
- **Usuário:** admin@open-metadata.org
- **Senha:** adminpostgres_simple

## Configuração do Banco de Dados (OpenMetadata)

Para configurar a conexão PostgreSQL no OpenMetadata:

1. Faça login no OpenMetadata
2. Configure a conexão PostgreSQL com os dados:
   - **Usuário:** airflow
   - **Tipo de Autenticação:** Basic Auth
   - **Senha:** airflow
   - **Host e Porta:** postgres_simple:5432
   - **Banco de Dados:** customer_db
   - **Configuração:** Ingest All Databases

## Limpeza (Importante)

⚠️ **Os containers ocupam muito espaço em disco. Execute a limpeza após o uso:**

```bash
./clean_docker_full.sh
```
