#!/bin/bash

echo "Parando e removendo todos os containers..."
docker stop $(docker ps -aq) 2>/dev/null || true
docker rm $(docker ps -aq) 2>/dev/null || true

echo "Removendo todos os volumes..."
docker volume prune -f
docker volume rm $(docker volume ls -q) 2>/dev/null || true

echo "Removendo todas as redes customizadas..."
docker network prune -f

echo "Removendo todas as imagens..."
docker image prune -af

echo "Limpeza completa do Docker finalizada!"
