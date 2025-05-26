#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail

# Проверяем, что передано ровно два адреса сервера через запятую
if [ $# -ne 1 ] || [ -z "$1" ]; then
    echo "Ошибка: Необходимо передать два адреса сервера через запятую."
    echo "Пример: $0 сервер1,сервер2"
    exit 1
fi

IFS=',' read -r var1 var2 <<< "$1"

# Запуск Python-скрипта
if [ -f ".env/bin/activate" ]; then
    echo -e "\nЗапуск Python-скрипта\n"
    source .env/bin/activate
    python3 server_selector/server_selector.py "$var1" "$var2"
    deactivate
else
    echo "[!] Ошибка: venv не создан!"
    exit 1
fi

# Проверка результата
if [ -f "inventory.yaml" ]; then
    echo -e "\nСодержимое inventory.yaml:"
    cat inventory.yaml
else
    echo "[!] Ошибка: inventory.yaml не создан!"
    exit 1
fi

# Запуск Ansible
echo -e "\n[*]Запуск Ansible для установки и настройки PostgreSQL..."
ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i inventory.yaml ./postgres_install/playbooks.yaml
