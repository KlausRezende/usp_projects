#!/bin/bash

echo "🐳 Construindo e iniciando os containers..."
docker-compose up --build

echo "📊 Para conectar no DBeaver use:"
echo "Host: localhost"
echo "Port: 5432"
echo "Database: mydb"
echo "Username: myuser"
echo "Password: mypassword"
