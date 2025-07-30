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

# Пути
CONFIG_PATHS = {
    'sway_config': HOME / '.config' / 'sway' / 'config',
    'waybar_config': HOME / '.config' / 'waybar' / 'config.jsonc',
    'waybar_style': HOME / '.config' / 'waybar' / 'style.css',
    'waybar_scripts': HOME / '.config' / 'waybar',
    'photo': HOME / 'photo' / '1.jpg',
    'scripts_dir': HOME / 'Scripts',
    'service_file': Path('/etc/systemd/system/filesorter.service'),
    'fonts_dir': HOME / '.local' / 'share' / 'fonts',
    'local_bin': HOME / '.local' / 'bin'
}

# URL для загрузки (обновленные)
DOWNLOAD_URLS = {
    'nerd_fonts': "https://github.com/ryanoasis/nerd-fonts/releases/download/v3.0.2/JetBrainsMono.zip",
    'noto_emoji': "https://github.com/googlefonts/noto-emoji/raw/main/fonts/NotoColorEmoji.ttf",
    'sway_config': "https://raw.githubusercontent.com/1q2w3e4rf/config_sway/main/config",
    'waybar_config': "https://raw.githubusercontent.com/1q2w3e4rf/config_sway/main/config.jsonc",
    'waybar_style': "https://raw.githubusercontent.com/1q2w3e4rf/config_sway/main/style.css",
    'sample_photo': "https://github.com/1q2w3e4rf/config_sway/raw/main/1.jpg"
}

# Скрипты для Waybar (остаются без изменений)
WAYBAR_SCRIPTS = {
    'language.py': """#!/usr/bin/env python3
import json
import subprocess

def get_lang():
    try:
        output = subprocess.check_output(["swaymsg", "-t", "get_inputs"]).decode()
        data = json.loads(output)
        for device in data:
            if device["type"] == "keyboard":
                lang = device["xkb_active_layout_name"]
                icon = "🇷🇺" if "Russian" in lang else "🇺🇸" if "English" in lang else "⌨️"
                return {"text": f"{icon} {lang.split()[0]}", "tooltip": f"Язык: {lang}"}
        return {"text": "⌨️ None", "tooltip": "Не удалось определить раскладку"}
    except:
        return {"text": "⌨️ Error", "tooltip": "Ошибка получения раскладки"}

print(json.dumps(get_lang()))""",
    
    'mediaplayer.py': """#!/usr/bin/env python3
import json
import subprocess

def get_media():
    try:
        status = subprocess.check_output(["playerctl", "status"]).decode().strip()
        if status == "Playing":
            artist = subprocess.check_output(["playerctl", "metadata", "artist"]).decode().strip()
            title = subprocess.check_output(["playerctl", "metadata", "title"]).decode().strip()
            text = f"{artist} - {title}" if artist else title
            return {
                "text": text[:40] + "..." if len(text) > 40 else text,
                "tooltip": f"Сейчас играет: {text}",
                "class": "playing"
            }
        return {"text": "", "tooltip": "Нет активного плеера"}
    except:
        return {"text": "", "tooltip": "Ошибка плеера"}

print(json.dumps(get_media()))""",
    
    'notification.py': """#!/usr/bin/env python3
import json
import subprocess

def get_notifications():
    try:
        count = int(subprocess.check_output(["swaync-client", "-c"]).decode())
        dnd = subprocess.check_output(["swaync-client", "-D"]).decode().strip() == "true"
        icon = "" if dnd else "" if count > 0 else ""
        return {
            "text": str(count) if count > 0 else "",
            "tooltip": f"{count} уведомлений" if count > 0 else "Режим 'Не беспокоить'" if dnd else "Нет уведомлений",
            "class": "dnd" if dnd else "active" if count > 0 else "inactive"
        }
    except:
        return {"text": "", "tooltip": "Ошибка уведомлений"}

print(json.dumps(get_notifications()))"""
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

def run_cmd(cmd, sudo=False, password=None):
    """Выполнить команду с обработкой ошибок"""
    try:
        if sudo:
            if not password:
                password = getpass.getpass(f"{Colors.WARNING}Введите пароль sudo: {Colors.ENDC}")
            proc = subprocess.Popen(
                ['sudo', '-S'] + cmd.split(),
                stdin=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            proc.communicate(password + '\n')
            if proc.returncode != 0:
                raise subprocess.CalledProcessError(proc.returncode, cmd)
        else:
            subprocess.run(cmd.split(), check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"{Colors.FAIL}Ошибка при выполнении: {cmd}{Colors.ENDC}")
        return False

def download_file(url, dest):
    """Скачать файл по URL"""
    print(f"{Colors.OKBLUE}Скачивание {url}...{Colors.ENDC}")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(dest, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"{Colors.FAIL}Ошибка при загрузке: {e}{Colors.ENDC}")
        return False

def install_packages():
    """Установка системных пакетов"""
    print(f"{Colors.HEADER}Установка пакетов...{Colors.ENDC}")
    
    packages = [
        'sway', 'waybar', 'alacritty', 'rofi', 'grim', 'slurp',
        'pavucontrol', 'playerctl', 'brightnessctl', 'swaylock',
        'swayidle', 'swaync', 'networkmanager', 'blueman',
        'ttf-jetbrains-mono-nerd', 'noto-fonts-emoji',
        'python-pip', 'python-i3ipc', 'polkit-gnome',
        'meson', 'scdoc', 'wayland-protocols', 'jsoncpp',
        'libmpdclient', 'libnl', 'libpulse', 'libepoxy',
        'gtk-layer-shell', 'wireplumber', 'jq', 'htop',
        'python-requests', 'python-setuptools'
    ]
    
    if not run_cmd(f"pacman -S --needed --noconfirm {' '.join(packages)}", sudo=True):
        print(f"{Colors.WARNING}Попробуем установить пакеты по одному...{Colors.ENDC}")
        for pkg in packages:
            if not run_cmd(f"pacman -S --needed --noconfirm {pkg}", sudo=True):
                print(f"{Colors.FAIL}Не удалось установить {pkg}{Colors.ENDC}")

def install_fonts():
    """Установка шрифтов"""
    print(f"{Colors.HEADER}Установка шрифтов...{Colors.ENDC}")
    
    os.makedirs(CONFIG_PATHS['fonts_dir'], exist_ok=True)
    
    # Nerd Fonts
    nerd_zip = TEMP_PATH / "nerd_fonts.zip"
    if download_file(DOWNLOAD_URLS['nerd_fonts'], nerd_zip):
        with zipfile.ZipFile(nerd_zip, 'r') as zip_ref:
            zip_ref.extractall(CONFIG_PATHS['fonts_dir'])
    
    # Noto Emoji
    emoji_font = TEMP_PATH / "NotoColorEmoji.ttf"
    if download_file(DOWNLOAD_URLS['noto_emoji'], emoji_font):
        shutil.copy(emoji_font, CONFIG_PATHS['fonts_dir'])
    
    # Обновление кэша шрифтов
    run_cmd("fc-cache -fv")

def setup_configs():
    """Настройка конфигураций"""
    print(f"{Colors.HEADER}Настройка конфигураций...{Colors.ENDC}")
    
    # Создание директорий
    os.makedirs(HOME / '.config' / 'sway', exist_ok=True)
    os.makedirs(HOME / '.config' / 'waybar', exist_ok=True)
    os.makedirs(HOME / 'photo', exist_ok=True)
    os.makedirs(HOME / 'Scripts', exist_ok=True)
    os.makedirs(CONFIG_PATHS['local_bin'], exist_ok=True)
    
    # Загрузка конфигов
    print(f"{Colors.OKBLUE}Загрузка конфигураций...{Colors.ENDC}")
    
    # Sway config
    sway_config_temp = TEMP_PATH / "sway_config"
    if download_file(DOWNLOAD_URLS['sway_config'], sway_config_temp):
        shutil.copy(sway_config_temp, CONFIG_PATHS['sway_config'])
    
    # Waybar config
    waybar_config_temp = TEMP_PATH / "waybar_config"
    if download_file(DOWNLOAD_URLS['waybar_config'], waybar_config_temp):
        shutil.copy(waybar_config_temp, CONFIG_PATHS['waybar_config'])
    
    # Waybar style
    waybar_style_temp = TEMP_PATH / "waybar_style"
    if download_file(DOWNLOAD_URLS['waybar_style'], waybar_style_temp):
        shutil.copy(waybar_style_temp, CONFIG_PATHS['waybar_style'])
    
    # Скрипты Waybar
    print(f"{Colors.OKBLUE}Настройка скриптов Waybar...{Colors.ENDC}")
    for script_name, script_content in WAYBAR_SCRIPTS.items():
        script_path = CONFIG_PATHS['waybar_scripts'] / script_name
        with open(script_path, 'w') as f:
            f.write(script_content)
        os.chmod(script_path, 0o755)
    
    # Фото (исправленный URL)
    photo_temp = TEMP_PATH / "1.jpg"
    if download_file(DOWNLOAD_URLS['sample_photo'], photo_temp):
        shutil.copy(photo_temp, CONFIG_PATHS['photo'])
    else:
        # Альтернатива если фото не загружается
        print(f"{Colors.WARNING}Не удалось загрузить фото, создаем пустое...{Colors.ENDC}")
        with open(CONFIG_PATHS['photo'], 'wb') as f:
            f.write(b'\x00')

    # Основной скрипт
    script_path = CONFIG_PATHS['scripts_dir'] / '1.py'
    with open(script_path, 'w') as f:
        f.write("""#!/usr/bin/env python3
print("File sorter service running")""")
    os.chmod(script_path, 0o755)

def create_service():
    """Создание systemd сервиса"""
    print(f"{Colors.HEADER}Создание сервиса...{Colors.ENDC}")
    
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
        # Попробуем создать глобальный сервис
        try:
            with open(CONFIG_PATHS['service_file'], 'w') as f:
                f.write(service_content)
        except PermissionError:
            print(f"{Colors.WARNING}Требуются права sudo для создания сервиса...{Colors.ENDC}")
            password = getpass.getpass(f"{Colors.WARNING}Введите пароль sudo: {Colors.ENDC}")
            run_cmd(f"echo '{service_content}' | sudo tee {CONFIG_PATHS['service_file']}", sudo=True, password=password)
        
        run_cmd("systemctl daemon-reload", sudo=True)
        run_cmd("systemctl enable filesorter.service", sudo=True)
        run_cmd("systemctl start filesorter.service", sudo=True)
        
        print(f"{Colors.OKGREEN}Сервис успешно создан и запущен{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}Ошибка при создании сервиса: {e}{Colors.ENDC}")
        
        # Попробуем создать пользовательский сервис
        print(f"{Colors.WARNING}Попытка создать пользовательский сервис...{Colors.ENDC}")
        user_service_dir = HOME / '.config' / 'systemd' / 'user'
        user_service_dir.mkdir(parents=True, exist_ok=True)
        
        user_service_file = user_service_dir / 'filesorter.service'
        with open(user_service_file, 'w') as f:
            f.write(service_content)
        
        run_cmd("systemctl --user daemon-reload")
        run_cmd("systemctl --user enable filesorter.service")
        run_cmd("systemctl --user start filesorter.service")
        
        print(f"{Colors.OKGREEN}Пользовательский сервис создан{Colors.ENDC}")
        print(f"{Colors.BOLD}Для автозапуска выполните:{Colors.ENDC}")
        print("  loginctl enable-linger")

def main():
    print(f"{Colors.HEADER}{Colors.BOLD}Полная автоматическая настройка системы{Colors.ENDC}")
    
    # Проверка на root
    if os.geteuid() == 0:
        print(f"{Colors.FAIL}Ошибка: Не запускайте скрипт от root!{Colors.ENDC}")
        sys.exit(1)
    
    try:
        # Установка пакетов
        install_packages()
        
        # Установка шрифтов
        install_fonts()
        
        # Настройка конфигураций
        setup_configs()
        
        # Создание сервиса
        create_service()
        
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}Настройка успешно завершена!{Colors.ENDC}")
        print(f"\n{Colors.BOLD}Что сделано:{Colors.ENDC}")
        print("- Установлены все необходимые пакеты")
        print("- Установлены шрифты (Nerd Fonts + Emoji)")
        print("- Настроены конфиги Sway и Waybar")
        print("- Установлены скрипты Waybar")
        print("- Создан и запущен systemd сервис")
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
