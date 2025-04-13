# Тестовое задание Potgress

Реализовать консольное приложение, которое будет устанавливать PostgreSQL на удаленный хост, настраивать и запускать.

Вводные: 2 сервера, один на Debian, второй на CentOS (AlmaLinux). На обоих серверах пользователю root подложен один и тот же открытый ssh ключ. У исполнителя есть закрытая часть ключа, с помощью которой он подключается.

## Алгоритм работы

1. Bash скрипт

* Принимает данные для входа на сервер
* Формирование Inventory.ini
* Запуск Ansible role "Select server"
* запуск Ansible role "Postgres install"  

2. Python "Select server"

* Установка подключения с помощью Paramiko
* Сбор метрик
* Выявление лучшего сервера
* Формирование Inventory.yaml для настройки postgres с помощью pyyaml

3. Ansible role "PostgreSQL"

* Установка подключения
* Установка PostgreSQL
* Настройка PostgreSQL
* Проверка подлючения

## Системные требования для запуска

OS: Linux
Bash
Python 3.9+
Ansible

## Запуск скпипта

Для запуска склонировать репозиторий.

```bash
git clone && cd "$(basename "$_" .git)"
```

Создать env для python скрипта и установить необходимые пакеты

```bash
python3 -m venv .env
source .env/bin/activate
pip install -r requirements.txt
```

Скачать ansible роли для установки и настройки.

```bash
ansible-galaxy role install geerlingguy.postgresql buluma.timezone
```

Затем сделать скрипт исполняемым. Запустить скрипт.

```bash
chmod +x up.sh
./up.sh ip-server-1, ip-server-2
```
