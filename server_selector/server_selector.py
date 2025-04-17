from paramiko import SSHClient, AutoAddPolicy
from sys import argv, stderr, exit
from yaml import safe_load, dump

SERVER_METRICS_INPUT = "CPU Load: {} %\nRAM Available: {} MB\nDisk I/O: {} %\nDisk Free: {} GB\nСумма очков: {}\n"
TEMPLATE_FILE = "server_selector/template/inventory_template.yaml"
REMOTE_USER="root"

def ssh_command(server, command):
    """Подключение к серверам"""
    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy())
    try:
        client.connect(
            hostname=server,
            username=REMOTE_USER,
            timeout=5
        )
        _, stdout, _ = client.exec_command(command)
        return stdout.read().decode().strip()
    except Exception as error:
        print(f"[!] Ошибка подключения к {server}: {error}", file=stderr)
        exit(1)
    finally:
        client.close()


def get_metrics(server):
    """Сбор метрик с помощью bash команд"""
    metrics = {
        'cpu_load': 0,
        'ram_available': 0,
        'disk_io': 0,
        'disk_free': 0
    }

    # CPU Load (1-min avg)
    cpu_load = ssh_command(
        server, "uptime | awk -F 'load average:' '{print $2}' | awk '{print $1}' | tr -d ','")
    metrics['cpu_load'] = float(cpu_load) if cpu_load else 999.0

    # Available RAM (MB)
    ram_available = ssh_command(server, "free -m | awk '/Mem:/ {print $7}'")
    metrics['ram_available'] = float(ram_available) if ram_available else 0.0

    # Disk I/O Utilization (%)
    disk_io = ssh_command(
        server, "iostat -d -x 1 2 | awk '/^[vsh]d/ {io=$NF} END {print io}'")
    metrics['disk_io'] = float(disk_io) if disk_io else 100.0

    # Free Disk Space on / (GB)
    disk_free = ssh_command(
        server, "df -BG / | awk 'NR==2 {print $4}' | tr -d 'G'")
    metrics['disk_free'] = float(disk_free) if disk_free else 0.0

    return metrics


def calculate_score(metrics):
    """Подсчет метрик в общие число очков"""
    return (
        0.4 * metrics['ram_available'] +
        0.3 * (100 - metrics['cpu_load'] * 10) +
        0.2 * (100 - metrics['disk_io']) +
        0.1 * metrics['disk_free']
    )


def generate_inventory(best_server, bad_server):
    """Генерация inventory.yaml на основе шаблона"""
    try:
        with open(TEMPLATE_FILE) as f:
            inventory = safe_load(f)

        inventory['best_server']['hosts'] = {best_server: None}
        inventory['all']['vars']['bad_server'] = bad_server

        with open("inventory.yaml", 'w') as f:
            dump(inventory, f, sort_keys=False, default_flow_style=False)
        print(f"[+] Inventory создан на основе {TEMPLATE_FILE}")
    except Exception as error:
        print(f"[!] Ошибка генерации inventory: {error}", file=stderr)
        exit(1)


if __name__ == "__main__":
    if len(argv) != 3:
        print("Использование: python server_selector/server_selector.py <server1> <server2>", file=stderr)
        exit(1)

    server1, server2 = argv[1], argv[2]
    servers = [server1, server2]
    scores = {}

    print("[*] Анализ серверов для PostgreSQL...\n")
    for server in servers:
        print(f"[*] Проверка {server}...")
        metrics = get_metrics(server)
        score = calculate_score(metrics)
        scores[server] = score
        print(SERVER_METRICS_INPUT.format(
            metrics['cpu_load'], metrics['ram_available'], metrics['disk_io'], metrics['disk_free'], score))

    best_server = max(scores, key=scores.get)
    bad_server = min(scores, key=scores.get)
    print(
        f"\n[*] Лучший сервер для PostgreSQL: {best_server} (Общие чесло очков: {scores[best_server]:.2f})")

    generate_inventory(best_server, bad_server)
