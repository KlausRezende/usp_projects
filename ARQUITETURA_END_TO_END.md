# Arquitetura End-to-End - Projeto USP

## Visão Geral da Arquitetura

Este projeto implementa uma arquitetura completa de Data Engineering com orquestração, processamento, qualidade de dados, governança e sistema de monitoramento com alertas automatizados.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           ARQUITETURA END-TO-END                                │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────────────────┐
│   DATA SOURCES  │    │   ORCHESTRATION  │    │        DATA PROCESSING          │
│                 │    │                  │    │                                 │
│ ┌─────────────┐ │    │ ┌──────────────┐ │    │ ┌─────────────────────────────┐ │
│ │ Bancos      │ │    │ │   AIRFLOW    │ │    │ │        SPARK JOBS           │ │
│ │ (.tsv)      │ │────┤ │              │ │────┤ │                             │ │
│ └─────────────┘ │    │ │ - Webserver  │ │    │ │ Bronze Layer (Raw Data)     │ │
│                 │    │ │ - Scheduler  │ │    │ │ ├─ tb_bz_bancos             │ │
│ ┌─────────────┐ │    │ │ - Executor   │ │    │ │ ├─ tb_bz_empregados         │ │
│ │ Empregados  │ │    │ │              │ │    │ │ └─ tb_bz_reclamacoes        │ │
│ │ (.csv)      │ │    │ │ Port: 8081   │ │    │ │                             │ │
│ └─────────────┘ │    │ └──────────────┘ │    │ │ Silver Layer (Cleaned)      │ │
│                 │    │                  │    │ │ ├─ tb_sv_bancos             │ │
│ ┌─────────────┐ │    │ ┌──────────────┐ │    │ │ ├─ tb_sv_empregados         │ │
│ │ Reclamações │ │    │ │ POSTGRES     │ │    │ │ └─ tb_sv_reclamacoes        │ │
│ │ (.csv)      │ │    │ │ (Airflow DB) │ │    │ │                             │ │
│ └─────────────┘ │    │ │              │ │    │ │ Gold Layer (Business)       │ │
│                 │    │ │ Port: 5432   │ │    │ │ └─ tb_gd_customer_detail    │ │
└─────────────────┘    │ └──────────────┘ │    │ └─────────────────────────────┘ │
                       └──────────────────┘    └─────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────────────────────┐
│                     DATA STORAGE, QUALITY & MONITORING                          │
│                                                                                 │
│ ┌─────────────────────────────┐    ┌─────────────────────────────────────────┐ │
│ │      POSTGRESQL             │    │           DATA QUALITY                  │ │
│ │    (Data Warehouse)         │    │                                         │ │
│ │                             │    │ ┌─────────────────────────────────────┐ │ │
│ │ Database: customer_db       │    │ │        GREAT EXPECTATIONS          │ │ │
│ │ Host: postgres_simple       │    │ │                                     │ │ │
│ │ Port: 5433                  │    │ │ - Data Validation Rules             │ │ │
│ │                             │    │ │ - Quality Metrics                   │ │ │
│ │ Tables:                     │    │ │ - Automated Reports                 │ │ │
│ │ ├─ Bronze Layer Tables      │    │ │ - Threshold Validation (>80%)       │ │ │
│ │ ├─ Silver Layer Tables      │    │ │                                     │ │ │
│ │ └─ Gold Layer Tables        │    │ │ Output: validation_results.txt      │ │ │
│ │                             │    │ └─────────────────────────────────────┘ │ │
│ └─────────────────────────────┘    │                    ↓                    │ │
│                                    │ ┌─────────────────────────────────────┐ │ │
│                                    │ │        MONITORING & ALERTS          │ │ │
│                                    │ │                                     │ │ │
│                                    │ │ ┌─────────────────────────────────┐ │ │ │
│                                    │ │ │          DISCORD BOT            │ │ │ │
│                                    │ │ │                                 │ │ │ │
│                                    │ │ │ Automated Notifications:        │ │ │ │
│                                    │ │ │ ❌ DQ Validation Failed         │ │ │ │
│                                    │ │ │ ✅ Pipeline Success             │ │ │ │
│                                    │ │ │ 📊 Quality Metrics Report       │ │ │ │
│                                    │ │ │ 🚨 Critical Failures            │ │ │ │
│                                    │ │ │                                 │ │ │ │
│                                    │ │ │ Trigger: DQ Percentage < 80%    │ │ │ │
│                                    │ │ └─────────────────────────────────┘ │ │ │
│                                    │ └─────────────────────────────────────┘ │ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        DATA GOVERNANCE & CATALOG                                │
│                                                                                 │
│ ┌─────────────────────────────────────────────────────────────────────────────┐ │
│ │                           OPENMETADATA                                      │ │
│ │                                                                             │ │
│ │ ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐ │ │
│ │ │   MYSQL DB      │  │  ELASTICSEARCH  │  │      WEB INTERFACE          │ │ │
│ │ │                 │  │                 │  │                             │ │ │
│ │ │ Metadata Store  │  │ Search Engine   │  │ - Data Discovery            │ │ │
│ │ │ Port: 3306      │  │ Port: 9200      │  │ - Lineage Tracking          │ │ │
│ │ │                 │  │                 │  │ - Schema Management         │ │ │
│ │ └─────────────────┘  │ └─────────────────┘  │ - Data Quality Dashboard    │ │ │
│ │                                             │ - User Management           │ │ │
│ │ ┌─────────────────────────────────────────┐ │                             │ │ │
│ │ │           INGESTION SERVICE             │ │ Port: 8585                  │ │ │
│ │ │                                         │ │                             │ │ │
│ │ │ - Automated Metadata Collection         │ │ Credentials:                │ │ │
│ │ │ - Schema Discovery                      │ │ User: admin@open-metadata.org│ │ │
│ │ │ - Data Profiling                        │ │ Pass: adminpostgres_simple  │ │ │
│ │ │ - Connection to PostgreSQL              │ └─────────────────────────────┘ │ │
│ │ │ Port: 8080                              │                               │ │
│ │ └─────────────────────────────────────────┘                               │ │
│ └─────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Componentes da Arquitetura

### 1. **Camada de Dados (Data Sources)**
- **Bancos**: Arquivo TSV com informações de instituições financeiras
- **Empregados**: Arquivos CSV com dados de funcionários (Glassdoor)
- **Reclamações**: Arquivos CSV trimestrais (2021-2022) com reclamações de clientes

### 2. **Orquestração (Apache Airflow)**
- **Webserver**: Interface web para monitoramento (porta 8081)
- **Scheduler**: Agendamento automático de pipelines (diário às 9h)
- **Executor**: Execução de tarefas
- **Database**: PostgreSQL para metadados do Airflow (porta 5432)

#### DAGs Implementados:
- `institution_detail_pipeline`: Pipeline principal de ETL
- `institution_detail_data_quality_pipeline`: Pipeline de qualidade de dados

### 3. **Processamento de Dados (Apache Spark)**

#### **Bronze Layer (Dados Brutos)**
- `tb_bz_bancos`: Dados brutos de bancos
- `tb_bz_empregados`: Dados brutos de empregados  
- `tb_bz_reclamacoes`: Dados brutos de reclamações

#### **Silver Layer (Dados Limpos)**
- `tb_sv_bancos`: Dados de bancos processados e limpos
- `tb_sv_empregados`: Dados de empregados processados
- `tb_sv_reclamacoes`: Dados de reclamações processados

#### **Gold Layer (Dados de Negócio)**
- `tb_gd_customer_detail`: Tabela consolidada com detalhes completos dos clientes

### 4. **Armazenamento (PostgreSQL)**
- **Database**: `customer_db`
- **Host**: `postgres_simple`
- **Porta**: 5433
- **Credenciais**: airflow/airflow

### 5. **Qualidade de Dados (Great Expectations)**
- Validação automatizada de dados
- Métricas de qualidade
- Threshold de aprovação: >80%
- Relatórios em `/opt/airflow/result/validation_results.txt`

### 6. **Sistema de Monitoramento e Alertas**

#### **Discord Integration**
- **Função**: `notification_discord()` em `libs/log.py`
- **Triggers Automáticos**:
  - ❌ **Falha na Validação DQ**: Quando percentual < 80%
  - 🚨 **Falhas Críticas**: Erros em DAGs principais
  - ✅ **Sucessos**: Confirmação de pipelines executados
  - 📊 **Relatórios**: Métricas de qualidade de dados

#### **Fluxo de Alertas**:
```
Data Quality Check → Percentage < 80% → Discord Alert → Team Notification
```

#### **Mensagens de Alerta**:
- `"❌ Data Quality validation failed - notifying team"`
- `"📊 Data Quality Results: {percentage}%"`
- Logs detalhados com contexto da falha

### 7. **Governança de Dados (OpenMetadata)**

#### **Componentes:**
- **MySQL**: Armazenamento de metadados (porta 3306)
- **Elasticsearch**: Motor de busca (porta 9200)
- **Web Interface**: Portal de governança (porta 8585)
- **Ingestion Service**: Coleta automática de metadados (porta 8080)

#### **Funcionalidades:**
- Descoberta automática de dados
- Rastreamento de linhagem
- Gerenciamento de esquemas
- Dashboard de qualidade de dados
- Catálogo de dados centralizado

## Fluxo de Execução

### 1. **Pipeline Principal (institution_detail_pipeline)**
```
Start → Bronze Tasks (Parallel) → Silver Tasks → Gold Task → Trigger DQ → End
```

### 2. **Pipeline de Qualidade com Monitoramento (institution_detail_data_quality_pipeline)**
```
Start → Data Quality Validation → Branch Decision → [Valid ✅ | Invalid ❌ + Discord Alert] → End
```

### 3. **Sistema de Alertas**
```
DQ Validation → Read Results → Check Threshold → Send Discord Alert → Raise Exception
```

### 4. **Dependências entre Camadas**
- **Bronze**: Execução paralela independente
- **Silver**: Depende da respectiva tabela Bronze
- **Gold**: Depende de todas as tabelas Silver
- **Data Quality**: Executado após Gold Layer
- **Alertas**: Disparados automaticamente em falhas

## Configuração e Acesso

### **Portas de Acesso:**
- Airflow: http://localhost:8081 (admin/admin)
- OpenMetadata: http://localhost:8585 (admin@open-metadata.org/adminpostgres_simple)
- PostgreSQL: localhost:5433 (airflow/airflow)
- Elasticsearch: localhost:9200
- MySQL: localhost:3306

### **Configuração OpenMetadata:**
- **Host**: postgres_simple:5432
- **Database**: customer_db
- **Usuário**: airflow
- **Senha**: airflow
- **Configuração**: Ingest All Databases

### **Configuração de Alertas:**
- **Discord Webhook**: Configurado em `libs/log.py`
- **Threshold DQ**: 80% (configurável em `parameters_institution_detail_data_quality.yaml`)
- **Callbacks**: `on_success_callback` e `on_failure_callback` em todas as DAGs

## Tecnologias Utilizadas

- **Containerização**: Docker & Docker Compose
- **Orquestração**: Apache Airflow
- **Processamento**: Apache Spark (PySpark)
- **Armazenamento**: PostgreSQL
- **Qualidade**: Great Expectations
- **Governança**: OpenMetadata
- **Busca**: Elasticsearch
- **Monitoramento**: Discord API
- **Linguagem**: Python 3.9

## Benefícios da Arquitetura

1. **Escalabilidade**: Arquitetura em camadas permite crescimento independente
2. **Observabilidade**: Monitoramento completo via Airflow e OpenMetadata
3. **Qualidade**: Validação automatizada com Great Expectations
4. **Alertas Proativos**: Notificações imediatas via Discord
5. **Governança**: Catálogo centralizado e rastreamento de linhagem
6. **Manutenibilidade**: Código modular e configuração via YAML
7. **Portabilidade**: Totalmente containerizada
8. **Confiabilidade**: Sistema de alertas garante resposta rápida a problemas

## Monitoramento e SLA

### **Métricas Monitoradas:**
- **Data Quality Score**: Percentual de validações bem-sucedidas
- **Pipeline Success Rate**: Taxa de sucesso das execuções
- **Processing Time**: Tempo de execução de cada camada
- **Data Freshness**: Atualização dos dados

### **Alertas Configurados:**
- **Crítico**: DQ < 80% → Discord imediato
- **Warning**: Falhas em tasks individuais
- **Info**: Sucessos e métricas regulares

## Limpeza e Manutenção

⚠️ **Importante**: Execute `./clean_docker_full.sh` após o uso para liberar espaço em disco.

Esta arquitetura implementa as melhores práticas de Data Engineering moderna, proporcionando um pipeline robusto, observável, governado e monitorado com alertas proativos para garantir a qualidade e confiabilidade dos dados institucionais.
