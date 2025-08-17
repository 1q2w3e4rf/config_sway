#!/usr/bin/env python3
import os
import subprocess
import shutil
import sys
import getpass
import requests
import tarfile
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory

# Конфигурация
USER = os.getenv('USER')
HOME = Path.home()
TEMP_DIR = TemporaryDirectory()
TEMP_PATH = Path(TEMP_DIR.name)

# Пути конфигов
CONFIG_PATHS = {
    'sway': HOME / '.config' / 'sway',
    'waybar': HOME / '.config' / 'waybar',
    'rofi': HOME / '.config' / 'rofi',
    'wlogout': HOME / '.config' / 'wlogout',
    'swaync': HOME / '.config' / 'swaync',
    'fonts': HOME / '.local' / 'share' / 'fonts',
    'bin': HOME / '.local' / 'bin',
    'photos': HOME / 'photos'
}

# URL репозитория с конфигами
CONFIG_REPO = "https://github.com/1q2w3e4rf/config_sway/archive/main.zip"

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

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

def install_yay():
    """Установка yay если не установлен"""
    if not shutil.which('yay'):
        print(f"{Colors.HEADER}Установка yay...{Colors.ENDC}")
        run_cmd("sudo pacman -S --needed --noconfirm git base-devel", sudo=True)
        os.chdir(TEMP_PATH)
        run_cmd("git clone https://aur.archlinux.org/yay.git")
        os.chdir(TEMP_PATH / "yay")
        run_cmd("makepkg -si --noconfirm")
        os.chdir(HOME)
    else:
        print(f"{Colors.OKGREEN}yay уже установлен{Colors.ENDC}")

def download_configs():
    """Скачивание и распаковка конфигов"""
    print(f"{Colors.HEADER}Загрузка конфигураций...{Colors.ENDC}")
    zip_path = TEMP_PATH / "configs.zip"
    
    # Скачивание архива
    try:
        response = requests.get(CONFIG_REPO, stream=True)
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    except Exception as e:
        print(f"{Colors.FAIL}Ошибка загрузки: {e}{Colors.ENDC}")
        return False

    # Распаковка
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(TEMP_PATH)
    
    # Путь к распакованным конфигам
    config_dir = TEMP_PATH / "config_sway-main"
    
    # Создание папок
    for path in CONFIG_PATHS.values():
        path.mkdir(parents=True, exist_ok=True)
    
    # Копирование конфигов
    shutil.copytree(config_dir / "sway", CONFIG_PATHS['sway'], dirs_exist_ok=True)
    shutil.copytree(config_dir / "waybar", CONFIG_PATHS['waybar'], dirs_exist_ok=True)
    shutil.copytree(config_dir / "rofi", CONFIG_PATHS['rofi'], dirs_exist_ok=True)
    shutil.copytree(config_dir / "wlogout", CONFIG_PATHS['wlogout'], dirs_exist_ok=True)
    shutil.copytree(config_dir / "swaync", CONFIG_PATHS['swaync'], dirs_exist_ok=True)
    
    # Установка прав на скрипты
    for script in (CONFIG_PATHS['waybar'].glob("*.py")):
        script.chmod(0o755)
    
    return True

def install_packages():
    """Установка пакетов через yay"""
    print(f"{Colors.HEADER}Установка пакетов...{Colors.ENDC}")
    
    packages = [
        'sway', 'waybar', 'alacritty', 'rofi', 'grim', 'slurp', 'wf-recorder',
        'pavucontrol', 'playerctl', 'brightnessctl', 'swaylock', 'swayidle',
        'swaync', 'networkmanager', 'blueman', 'nmtui', 'wlogout',
        'ttf-jetbrains-mono-nerd', 'noto-fonts-emoji', 'ttf-dejavu', 
        'python-pip', 'python-i3ipc', 'polkit-gnome', 'wl-clipboard', 'clipman',
        'qt5-wayland', 'qt6-wayland', 'mpv', 'imv', 'zathura', 'thunar'
    ]
    
    # Установка основных пакетов
    run_cmd(f"yay -S --needed --noconfirm {' '.join(packages)}")
    
    # Установка AUR пакетов если нужно
    aur_packages = ['libinput-gestures', 'python-pywayland']
    for pkg in aur_packages:
        run_cmd(f"yay -S --needed --noconfirm {pkg}")

def setup_autostart():
    """Настройка автозапуска"""
    print(f"{Colors.HEADER}Настройка автозапуска...{Colors.ENDC}")
    
    autostart = CONFIG_PATHS['sway'] / "autostart"
    with open(autostart, 'w') as f:
        f.write("""#!/bin/bash
# Автозапуск приложений
swayidle -w \\
    timeout 300 'swaylock -f -c 000000' \\
    timeout 600 'swaymsg "output * dpms off"' \\
    resume 'swaymsg "output * dpms on"' \\
    before-sleep 'swaylock -f -c 000000' &

swaync &
nm-applet --indicator &
blueman-applet &
/usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1 &
wl-paste -t text --watch clipman store &
""")
    autostart.chmod(0o755)

def main():
    print(f"{Colors.HEADER}{Colors.BOLD}Автоматическая настройка Sway/Waybar{Colors.ENDC}")
    
    # Проверка на root
    if os.geteuid() == 0:
        print(f"{Colors.FAIL}Ошибка: Не запускайте скрипт от root!{Colors.ENDC}")
        sys.exit(1)
    
    try:
        # 1. Установка yay
        install_yay()
        
        # 2. Загрузка конфигов
        if not download_configs():
            sys.exit(1)
        
        # 3. Установка пакетов
        install_packages()
        
        # 4. Настройка автозапуска
        setup_autostart()
        
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}Настройка успешно завершена!{Colors.ENDC}")
        print(f"\n{Colors.BOLD}Что сделано:{Colors.ENDC}")
        print("- Установлен yay (менеджер AUR пакетов)")
        print("- Загружены и размещены все конфиги")
        print("- Установлены все необходимые пакеты")
        print("- Настроен автозапуск сервисов")
        print(f"\n{Colors.BOLD}Перезагрузите систему для применения изменений{Colors.ENDC}")
    
    except KeyboardInterrupt:
        print(f"\n{Colors.FAIL}Прервано пользователем{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.FAIL}Критическая ошибка: {e}{Colors.ENDC}")
        sys.exit(1)
    finally:
        TEMP_DIR.cleanup()

if __name__ == "__main__":
    main()
