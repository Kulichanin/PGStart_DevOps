#!/bin/bash

if [ $# -ne 2 ]; then
    echo "Использование: $0 root@ip1 root@ip2"
    exit 1
fi

# Запуск Python-скрипта
if [ -f ".env/bin/activate" ]; then
    echo -e "\nЗапуск Python-скрипта"
    python3 server_selector/pg_server_selector.py "$1" "$2"
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
ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i inventory.yaml ./postgres_install/playbooks.yaml