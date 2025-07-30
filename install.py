#!/usr/bin/env python3
import os
import subprocess
import shutil
import sys
from pathlib import Path

# Получаем имя текущего пользователя
USER = os.getenv('USER')
HOME = Path.home()

# Пути для конфигурации
CONFIG_PATHS = {
    'sway_config': HOME / '.config' / 'sway' / 'config',
    'waybar_dir': HOME / '.config' / 'waybar',
    'photo_dir': HOME / 'photo',
    'scripts_dir': HOME / 'Scripts',
    'service_file': Path('/etc/systemd/system/filesorter.service')
}

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def run_cmd(cmd, sudo=False):
    """Выполнить команду с обработкой ошибок"""
    try:
        if sudo:
            subprocess.run(['sudo'] + cmd.split(), check=True)
        else:
            subprocess.run(cmd.split(), check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"{Colors.FAIL}Ошибка при выполнении: {cmd}{Colors.ENDC}")
        return False

def create_dirs():
    """Создание всех необходимых директорий"""
    print(f"{Colors.HEADER}Создание директорий...{Colors.ENDC}")
    
    dirs_to_create = [
        HOME / '.config' / 'sway',
        CONFIG_PATHS['waybar_dir'],
        CONFIG_PATHS['photo_dir'],
        CONFIG_PATHS['scripts_dir']
    ]
    
    for directory in dirs_to_create:
        try:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"{Colors.OKBLUE}Создана директория: {directory}{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.FAIL}Ошибка при создании {directory}: {e}{Colors.ENDC}")
            sys.exit(1)

def copy_files():
    """Копирование всех необходимых файлов"""
    print(f"{Colors.HEADER}Копирование файлов...{Colors.ENDC}")
    
    # Предполагаем, что скрипт запускается из директории с файлами
    current_dir = Path(__file__).parent
    
    try:
        # Sway config
        shutil.copy('config', CONFIG_PATHS['sway_config'])
        print(f"{Colors.OKBLUE}Скопирован sway config{Colors.ENDC}")
        
        # Waybar configs
        shutil.copy('config.jsonc', CONFIG_PATHS['waybar_dir'] / 'config.jsonc')
        shutil.copy('style.css', CONFIG_PATHS['waybar_dir'] / 'style.css')
        print(f"{Colors.OKBLUE}Скопированы waybar configs{Colors.ENDC}")
        
        # Скрипты для waybar (кроме 1.py)
        for script in current_dir.glob('*.py'):
            if script.name != '1.py':
                shutil.copy(script, CONFIG_PATHS['waybar_dir'])
                # Даем права на выполнение
                os.chmod(CONFIG_PATHS['waybar_dir'] / script.name, 0o755)
        print(f"{Colors.OKBLUE}Скопированы скрипты для waybar{Colors.ENDC}")
        
        # Фото
        shutil.copy('1.jpg', CONFIG_PATHS['photo_dir'] / '1.jpg')
        print(f"{Colors.OKBLUE}Скопировано фото{Colors.ENDC}")
        
        # Скрипт 1.py в Scripts
        shutil.copy('1.py', CONFIG_PATHS['scripts_dir'] / '1.py')
        os.chmod(CONFIG_PATHS['scripts_dir'] / '1.py', 0o755)
        print(f"{Colors.OKBLUE}Скопирован 1.py в Scripts{Colors.ENDC}")
        
    except Exception as e:
        print(f"{Colors.FAIL}Ошибка при копировании файлов: {e}{Colors.ENDC}")
        sys.exit(1)

def create_service():
    """Создание и активация systemd сервиса"""
    print(f"{Colors.HEADER}Создание systemd сервиса...{Colors.ENDC}")
    
    service_content = f"""[Unit]
Description=File Sorter Service
After=network.target

[Service]
Type=simple
User={USER}
ExecStart=/usr/bin/python3 {CONFIG_PATHS['scripts_dir']}/1.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""
    
    try:
        with open(CONFIG_PATHS['service_file'], 'w') as f:
            f.write(service_content)
        
        run_cmd('systemctl daemon-reload', sudo=True)
        run_cmd('systemctl enable filesorter.service', sudo=True)
        run_cmd('systemctl start filesorter.service', sudo=True)
        
        print(f"{Colors.OKGREEN}Сервис успешно создан и активирован{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}Ошибка при создании сервиса: {e}{Colors.ENDC}")
        sys.exit(1)

def main():
    print(f"{Colors.HEADER}{Colors.BOLD}Начало автоматической настройки{Colors.ENDC}")
    
    # Проверка на root
    if os.geteuid() == 0:
        print(f"{Colors.FAIL}Ошибка: Не запускайте скрипт от root!{Colors.ENDC}")
        sys.exit(1)
    
    # Основные шаги
    create_dirs()
    copy_files()
    create_service()
    
    print(f"\n{Colors.OKGREEN}{Colors.BOLD}Настройка успешно завершена!{Colors.ENDC}")
    print(f"\n{Colors.BOLD}Что сделано:{Colors.ENDC}")
    print(f"- Созданы все необходимые директории")
    print(f"- Скопированы конфиги Sway и Waybar")
    print(f"- Скопированы все скрипты (включая 1.py в ~/Scripts)")
    print(f"- Создан и активирован systemd сервис для 1.py")
    print(f"\n{Colors.BOLD}Сервис можно проверить командами:{Colors.ENDC}")
    print(f"  systemctl status filesorter.service")
    print(f"  journalctl -u filesorter.service -f")

if __name__ == "__main__":
    main()
