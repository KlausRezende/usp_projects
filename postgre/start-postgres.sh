#!/bin/bash

echo "Iniciando PostgreSQL simples..."

# Para o compose atual se estiver rodando
docker compose down 2>/dev/null

# Inicia o PostgreSQL simples
docker compose -f docker-compose-simple.yml up -d

echo ""
echo "PostgreSQL iniciado!"
echo "Conexão:"
echo "  Host: localhost"
echo "  Porta: 5432"
echo "  Database: testdb"
echo "  Usuário: postgres"
echo "  Senha: 123456"
echo ""
echo "Para parar: docker compose -f docker-compose-simple.yml down"
