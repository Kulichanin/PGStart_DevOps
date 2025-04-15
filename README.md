# Тестовое задание Potgress

Реализовать консольное приложение, которое будет устанавливать PostgreSQL на удаленный хост, настраивать и запускать.

Вводные: 2 сервера, один на Debian, второй на CentOS (AlmaLinux). На обоих серверах пользователю root подложен один и тот же открытый ssh ключ. У исполнителя есть закрытая часть ключа, с помощью которой он подключается.

## Алгоритм работы

1. Bash-скрипт принимает данные для входа на сервер.
2. Запускает Python-скрипт `server_selector/server_selector.py <server1> <server2>`.
    * Подключается с помощью [paramiko](https://www.paramiko.org/) к северам и получается метрики.
    * Выбирает лучший сервер.
    * С помощью [PyYAML](https://pypi.org/project/PyYAML/) формирует на основе выбора `inventory.yaml` для Ansible.  
3. Используя `inventory.yaml` запускает Ansible для настройки сервера.
    * Ansible role [buluma.timezone](https://galaxy.ansible.com/ui/standalone/roles/buluma/timezone/documentation/) настраивает корректное время(Полезно для сбора и обработки логов и метрик).
    * Ansible role [geerlingguy.postgresql](https://github.com/geerlingguy/ansible-role-postgresql)

## Алгоритм выбора сервера

Сбор метрик:
    - **CPU Load**: Нагрузка в течение 1 минуты (чем меньше, тем лучше).
    - **RAM Available**: Свободная память в MB (чем больше, тем лучше).
    - **Disk I/O**: Утилизация диска в % (чем меньше, тем лучше).
    - **Disk Free**: Свободное место на `/` в GB (чем больше, тем лучше).

Также необходимо понимать, что скрипт учитывает [нюансы](https://habr.com/ru/companies/otus/articles/521486/) работы СУБД **PostgreSQL**:
    - **Диск I/O**: Критичен для производительности БД, поэтому учитывается в формуле.
    - **RAM**: Чем больше свободной памяти, тем лучше для кэширования запросов.
    - **CPU**: Вторичен по сравнению с RAM и I/O, но влияет на параллельные запросы.

## Системные требования для запуска

Для машины на которой запускается скрипт:

OS: Linux
Bash
Python [3.9] +
Ansible [core 2.16.12] +

Для виртуальных машин необходимо наличие следующих утилит:
    - `df`
    - `free`
    - `awk`
    - `iostat`

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
chmod u+x ./up.sh
./up.sh ip-server-1, ip-server-2
```
