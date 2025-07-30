
#!/usr/bin/env python3
import os
import subprocess
import shutil
import sys
from pathlib import Path

# Конфигурация
USER = os.getenv('USER')
HOME = Path.home()
CONFIG_DIR = HOME / '.config'
SWAY_CONFIG = CONFIG_DIR / 'sway'
WAYBAR_CONFIG = CONFIG_DIR / 'waybar'
FONT_DIR = HOME / '.local' / 'share' / 'fonts'
FONTCONFIG_DIR = HOME / '.config' / 'fontconfig'

# Цвета для вывода
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

def install_packages():
    """Установка необходимых пакетов"""
    print(f"{Colors.HEADER}Установка основных пакетов...{Colors.ENDC}")
    packages = [
        'sway', 'waybar', 'alacritty', 'rofi', 'grim', 'slurp',
        'pavucontrol', 'playerctl', 'light', 'swaylock', 'swayidle',
        'swaync', 'networkmanager', 'bluez', 'blueman',
        'ttf-jetbrains-mono-nerd', 'noto-fonts-emoji',
        'python-pip', 'python-i3ipc', 'polkit-gnome'
    ]
    
    if not run_cmd(f"pacman -S --needed --noconfirm {' '.join(packages)}", sudo=True):
        sys.exit(1)

def install_fonts():
    """Установка дополнительных шрифтов"""
    print(f"{Colors.HEADER}Установка шрифтов...{Colors.ENDC}")
    os.makedirs(FONT_DIR, exist_ok=True)
    
    # Скачивание шрифтов
    fonts = [
        "https://github.com/ryanoasis/nerd-fonts/releases/download/v3.0.2/JetBrainsMono.zip",
        "https://github.com/googlefonts/noto-emoji/raw/main/fonts/NotoColorEmoji.ttf"
    ]
    
    for font in fonts:
        run_cmd(f"wget -P {FONT_DIR} {font}")
    
    # Распаковка архивов
    for font_file in FONT_DIR.glob('*.zip'):
        run_cmd(f"unzip -o {font_file} -d {FONT_DIR}")
        os.remove(font_file)
    
    # Обновление кэша шрифтов
    run_cmd("fc-cache -fv")

def copy_configs():
    """Копирование конфигурационных файлов"""
    print(f"{Colors.HEADER}Копирование конфигураций...{Colors.ENDC}")
    
    # Создание резервных копий существующих конфигов
    for config in [SWAY_CONFIG, WAYBAR_CONFIG]:
        if config.exists():
            backup = f"{config}.bak"
            print(f"{Colors.WARNING}Создание резервной копии {config} в {backup}{Colors.ENDC}")
            shutil.move(config, backup)
    
    # Копирование новых конфигов
    shutil.copytree('config', SWAY_CONFIG)
    shutil.copytree('waybar', WAYBAR_CONFIG)
    
    # Установка прав
    for script in (SWAY_CONFIG / 'scripts').glob('*.py'):
        script.chmod(0o755)

def setup_services():
    """Настройка сервисов автозагрузки"""
    print(f"{Colors.HEADER}Настройка сервисов...{Colors.ENDC}")
    
    # Polkit agent для прав sudo
    autostart_dir = CONFIG_DIR / 'autostart'
    os.makedirs(autostart_dir, exist_ok=True)
    
    with open(autostart_dir / 'polkit.desktop', 'w') as f:
        f.write("""[Desktop Entry]
Name=Polkit Agent
Exec=/usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1
Type=Application
""")

def final_steps():
    """Завершающие шаги установки"""
    print(f"\n{Colors.OKGREEN}Установка завершена успешно!{Colors.ENDC}")
    print(f"\n{Colors.BOLD}Что делать дальше:{Colors.ENDC}")
    print("1. Добавьте строку в ~/.bash_profile или ~/.zprofile:")
    print(f"   {Colors.OKBLUE}export XDG_CURRENT_DESKTOP=sway{Colors.ENDC}")
    print("2. Для входа в Sway выполните:")
    print(f"   {Colors.OKBLUE}sway{Colors.ENDC}")
    print("3. Или настройте вход через display manager")

def main():
    print(f"{Colors.HEADER}{Colors.BOLD}Начало автоматической установки Sway WM{Colors.ENDC}")
    
    # Проверка на Arch Linux
    if not Path('/etc/arch-release').exists():
        print(f"{Colors.FAIL}Ошибка: Этот скрипт работает только на Arch Linux!{Colors.ENDC}")
        sys.exit(1)
    
    # Проверка прав root
    if os.geteuid() == 0:
        print(f"{Colors.FAIL}Ошибка: Не запускайте скрипт от root!{Colors.ENDC}")
        sys.exit(1)
    
    # Основные шаги установки
    install_packages()
    install_fonts()
    copy_configs()
    setup_services()
    final_steps()

if __name__ == "__main__":
    main()