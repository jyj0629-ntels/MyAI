#!/bin/bash

ROOT="/APPDATA/MyAI"
BACKUP_DIR="${ROOT}/backupfile"

mkdir -p "${BACKUP_DIR}"

echo "=================================================="
echo "MyAI Backup Start"
echo "=================================================="
echo "ROOT=${ROOT}"
echo "BACKUP_DIR=${BACKUP_DIR}"

#--------------------------------------------------
# Server Information
#--------------------------------------------------

{
echo "=================================================="
echo "MYAI SERVER INFORMATION"
echo "=================================================="

echo
echo "GENERATED_AT"
date

echo
echo "=================================================="
echo "HOSTNAME"
echo "=================================================="
hostname

echo
echo "=================================================="
echo "OS RELEASE"
echo "=================================================="
cat /etc/os-release

echo
echo "=================================================="
echo "KERNEL"
echo "=================================================="
uname -a

echo
echo "=================================================="
echo "HOST INFO"
echo "=================================================="
hostnamectl 2>/dev/null

echo
echo "=================================================="
echo "CPU"
echo "=================================================="
lscpu

echo
echo "=================================================="
echo "MEMORY"
echo "=================================================="
free -h

echo
echo "=================================================="
echo "MEMINFO"
echo "=================================================="
head -30 /proc/meminfo

echo
echo "=================================================="
echo "DISK"
echo "=================================================="
lsblk

echo
echo "=================================================="
echo "DISK USAGE"
echo "=================================================="
df -h

echo
echo "=================================================="
echo "NETWORK"
echo "=================================================="
ip addr 2>/dev/null

echo
echo "=================================================="
echo "PORT"
echo "=================================================="
ss -tulnp 2>/dev/null

echo
echo "=================================================="
echo "HOST PYTHON"
echo "=================================================="
python --version 2>&1
python3 --version 2>&1

echo
which python
which python3

echo
echo "=================================================="
echo "DOCKER VERSION"
echo "=================================================="
docker version 2>/dev/null

echo
echo "=================================================="
echo "DOCKER COMPOSE"
echo "=================================================="
docker compose version 2>/dev/null

echo
echo "=================================================="
echo "DOCKER CONTAINERS"
echo "=================================================="
docker ps -a 2>/dev/null

echo
echo "=================================================="
echo "CONTAINER PYTHON"
echo "=================================================="
docker exec myai-api python --version 2>/dev/null

echo
echo "=================================================="
echo "POSTGRES VERSION"
echo "=================================================="
docker exec myai-postgres psql --version 2>/dev/null

echo
echo "=================================================="
echo "OLLAMA MODELS"
echo "=================================================="
docker exec ollama ollama list 2>/dev/null

echo
echo "=================================================="
echo "GIT REMOTE"
echo "=================================================="
git -C "${ROOT}" remote -v

echo
echo "=================================================="
echo "GIT BRANCH"
echo "=================================================="
git -C "${ROOT}" branch -a

echo
echo "=================================================="
echo "GIT STATUS"
echo "=================================================="
git -C "${ROOT}" status

echo
echo "=================================================="
echo "LAST COMMITS"
echo "=================================================="
git -C "${ROOT}" log --oneline -20

} > "${BACKUP_DIR}/MyAI_ServerInfo.txt"

#--------------------------------------------------
# Docker Status
#--------------------------------------------------

docker ps -a \
> "${BACKUP_DIR}/DockerContainers.txt" 2>&1

#--------------------------------------------------
# Directory Tree
#--------------------------------------------------

tree "${ROOT}" \
-I "__pycache__|*.pyc|.git|node_modules|backupfile" \
> "${BACKUP_DIR}/DirectoryTree.txt"

#--------------------------------------------------
# Source Dump
#--------------------------------------------------

cd "${ROOT}"

{
echo "=================================================="
echo "PROJECT TREE"
echo "=================================================="
tree -L 10

echo
echo "=================================================="
echo "DOCKERFILE"
echo "=================================================="
cat Dockerfile

echo
echo "=================================================="
echo "DOCKER-COMPOSE"
echo "=================================================="
cat docker-compose.yml

echo
echo "=================================================="
echo "REQUIREMENTS"
echo "=================================================="
cat requirements.txt

echo
echo "=================================================="
echo "SOURCE FILES"
echo "=================================================="

find app -name "*.py" | sort | while read f
do
    echo
    echo "##################################################"
    echo "FILE: $f"
    echo "##################################################"
    cat "$f"
done

echo
echo "=================================================="
echo "ALEMBIC"
echo "=================================================="

find alembic -name "*.py" | sort | while read f
do
    echo
    echo "##################################################"
    echo "FILE: $f"
    echo "##################################################"
    cat "$f"
done

} > "${BACKUP_DIR}/MyAI_FullSourceDump.txt"

#--------------------------------------------------
# PostgreSQL Backup
#--------------------------------------------------

docker exec myai-postgres pg_dump \
-U myai \
-d myai \
--clean \
--if-exists \
> "${BACKUP_DIR}/myai_postgres.sql" 2>/dev/null

#--------------------------------------------------
# Ollama Models
#--------------------------------------------------

docker exec ollama ollama list \
> "${BACKUP_DIR}/OllamaModels.txt" 2>/dev/null

echo
echo "=================================================="
echo "MyAI Backup Complete"
echo "=================================================="

echo
echo "Generated Files:"
ls -lh "${BACKUP_DIR}"
