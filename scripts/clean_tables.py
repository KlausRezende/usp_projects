#!/usr/bin/env python3
import psycopg2
import sys

def clean_all_tables():
    # Try different connection configurations
    connection_configs = [
        {"host": "localhost", "port": 5433, "database": "customer_db"},
        {"host": "localhost", "port": 5432, "database": "customer_db"},
        {"host": "postgres_simple", "port": 5432, "database": "customer_db"}
    ]
    
    conn = None
    for config in connection_configs:
        try:
            conn = psycopg2.connect(
                host=config["host"],
                port=config["port"],
                database=config["database"],
                user="airflow",
                password="airflow"
            )
            print(f"✅ Connected to {config['host']}:{config['port']}")
            break
        except Exception as e:
            print(f"❌ Failed to connect to {config['host']}:{config['port']} - {e}")
            continue
    
    if not conn:
        print("❌ Could not connect to any database. Make sure Docker containers are running.")
        sys.exit(1)
    
    cursor = conn.cursor()
    
    tables = [
        "tb_bz_bancos",
        "tb_bz_empregados", 
        "tb_bz_reclamacoes",
        "tb_sv_bancos",
        "tb_sv_empregados",
        "tb_sv_reclamacoes", 
        "tb_gd_institution_detail"
    ]
    
    for table in tables:
        try:
            cursor.execute(f"TRUNCATE TABLE {table} CASCADE;")
            print(f"✅ Cleaned table: {table}")
        except Exception as e:
            print(f"❌ Error cleaning {table}: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()
    print("🧹 All tables cleaned successfully!")

if __name__ == "__main__":
    clean_all_tables()
