#!/usr/bin/env python3
import os
import subprocess
import shutil
import sys
import getpass
import requests
import tarfile
import zipfile
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from datetime import datetime, timedelta

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
    'local_bin': HOME / '.local' / 'bin',
    'fonts_dir': HOME / '.local' / 'share' / 'fonts',
    'rofi_config': HOME / '.config' / 'rofi' / 'config.rasi',
    'alacritty_config': HOME / '.config' / 'alacritty' / 'alacritty.toml'
}

# URL для загрузки
DOWNLOAD_URLS = {
    'nerd_fonts': "https://github.com/ryanoasis/nerd-fonts/releases/download/v3.0.2/JetBrainsMono.zip",
    'noto_emoji': "https://github.com/googlefonts/noto-emoji/raw/main/fonts/NotoColorEmoji.ttf",
    'sway_config': "https://raw.githubusercontent.com/1q2w3e4rf/config_sway/main/config",
    'waybar_config': "https://raw.githubusercontent.com/1q2w3e4rf/config_sway/main/config.jsonc",
    'waybar_style': "https://raw.githubusercontent.com/1q2w3e4rf/config_sway/main/style.css",
    'sample_photo': "https://github.com/1q2w3e4rf/config_sway/raw/main/1.jpg",
    'rofi_config': "https://raw.githubusercontent.com/1q2w3e4rf/config_sway/main/config.rasi"
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

def format_size(size):
    """Форматирование размера в читаемый вид"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"

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

def download_file_with_progress(url, dest):
    """Скачать файл по URL с отображением прогресса"""
    print(f"{Colors.OKBLUE}Скачивание {url}...{Colors.ENDC}")
    try:
        start_time = time.time()
        last_print = start_time
        downloaded = 0
        
        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))
            
            with open(dest, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        now = time.time()
                        if now - last_print >= 1.0:  # Обновляем каждую секунду
                            elapsed = now - start_time
                            speed = downloaded / elapsed if elapsed > 0 else 0
                            remaining = (total_size - downloaded) / speed if speed > 0 else 0
                            
                            # Форматируем оставшееся время
                            if remaining > 3600:
                                remaining_str = str(timedelta(seconds=int(remaining)))
                            elif remaining > 60:
                                remaining_str = f"{int(remaining // 60)} мин {int(remaining % 60)} сек"
                            else:
                                remaining_str = f"{int(remaining)} сек"
                            
                            progress = (downloaded / total_size) * 100 if total_size > 0 else 0
                            print(
                                f"\rПрогресс: {progress:.1f}% | "
                                f"Скачано: {format_size(downloaded)} / {format_size(total_size)} | "
                                f"Скорость: {format_size(speed)}/сек | "
                                f"Осталось: {remaining_str}",
                                end='', flush=True
                            )
                            last_print = now
            
            print()  # Новая строка после завершения загрузки
            return True
            
    except requests.exceptions.RequestException as e:
        print(f"\n{Colors.FAIL}Ошибка при загрузке: {e}{Colors.ENDC}")
        return False
    except Exception as e:
        print(f"\n{Colors.FAIL}Неизвестная ошибка: {e}{Colors.ENDC}")
        return False

def install_yay():
    """Установка yay если его нет"""
    print(f"{Colors.HEADER}Проверка yay...{Colors.ENDC}")
    if not shutil.which('yay'):
        print(f"{Colors.OKBLUE}Установка yay...{Colors.ENDC}")
        run_cmd("sudo pacman -S --needed --noconfirm git base-devel")
        run_cmd("git clone https://aur.archlinux.org/yay.git /tmp/yay")
        os.chdir("/tmp/yay")
        run_cmd("makepkg -si --noconfirm")
        os.chdir(HOME)
        print(f"{Colors.OKGREEN}yay установлен{Colors.ENDC}")
    else:
        print(f"{Colors.OKGREEN}yay уже установлен{Colors.ENDC}")

def install_packages():
    """Установка системных пакетов через yay"""
    print(f"{Colors.HEADER}Установка пакетов...{Colors.ENDC}")
    
    packages = [
        'sway', 'waybar', 'alacritty', 'rofi', 'grim', 'slurp',
        'pavucontrol', 'playerctl', 'brightnessctl', 'swaylock',
        'swayidle', 'networkmanager', 'blueman',
        'ttf-jetbrains-mono-nerd', 'noto-fonts-emoji',
        'python-pip', 'python-i3ipc', 'polkit-gnome',
        'meson', 'scdoc', 'wayland-protocols', 'jsoncpp',
        'libmpdclient', 'libnl', 'libpulse', 'libepoxy',
        'gtk-layer-shell', 'wireplumber', 'jq', 'htop',
        'python-requests', 'python-setuptools', 'wf-recorder',
        'nwg-look-bin', 'swaybg', 'mako',
        'wl-clipboard', 'imv', 'zathura', 'zathura-pdf-mupdf',
        'qt5-wayland', 'qt6-wayland', 'xdg-desktop-portal-wlr',
        'libappindicator-gtk3', 'libnotify', 'pamixer',
        'light', 'bluez', 'bluez-utils', 'pulseaudio-bluetooth'
    ]
    
    if not run_cmd(f"yay -S --needed --noconfirm {' '.join(packages)}"):
        print(f"{Colors.WARNING}Попробуем установить пакеты по одному...{Colors.ENDC}")
        for pkg in packages:
            if not run_cmd(f"yay -S --needed --noconfirm {pkg}"):
                print(f"{Colors.FAIL}Не удалось установить {pkg}{Colors.ENDC}")

def install_fonts():
    """Установка шрифтов"""
    print(f"{Colors.HEADER}Установка шрифтов...{Colors.ENDC}")
    
    os.makedirs(CONFIG_PATHS['fonts_dir'], exist_ok=True)
    
    # Nerd Fonts
    nerd_zip = TEMP_PATH / "nerd_fonts.zip"
    if download_file_with_progress(DOWNLOAD_URLS['nerd_fonts'], nerd_zip):
        with zipfile.ZipFile(nerd_zip, 'r') as zip_ref:
            zip_ref.extractall(CONFIG_PATHS['fonts_dir'])
    
    # Noto Emoji
    emoji_font = TEMP_PATH / "NotoColorEmoji.ttf"
    if download_file_with_progress(DOWNLOAD_URLS['noto_emoji'], emoji_font):
        shutil.copy(emoji_font, CONFIG_PATHS['fonts_dir'])
    
    # Обновление кэша шрифтов
    run_cmd("fc-cache -fv")

def setup_configs():
    """Настройка конфигураций"""
    print(f"{Colors.HEADER}Настройка конфигураций...{Colors.ENDC}")
    
    # Создание директорий
    os.makedirs(HOME / '.config' / 'sway', exist_ok=True)
    os.makedirs(HOME / '.config' / 'waybar', exist_ok=True)
    os.makedirs(HOME / '.config' / 'rofi', exist_ok=True)
    os.makedirs(HOME / '.config' / 'alacritty', exist_ok=True)
    os.makedirs(HOME / 'photo', exist_ok=True)
    os.makedirs(CONFIG_PATHS['local_bin'], exist_ok=True)
    
    # Загрузка конфигов
    print(f"{Colors.OKBLUE}Загрузка конфигураций...{Colors.ENDC}")
    
    # Sway config
    sway_config_temp = TEMP_PATH / "sway_config"
    if download_file_with_progress(DOWNLOAD_URLS['sway_config'], sway_config_temp):
        shutil.copy(sway_config_temp, CONFIG_PATHS['sway_config'])
    
    # Waybar config
    waybar_config_temp = TEMP_PATH / "waybar_config"
    if download_file_with_progress(DOWNLOAD_URLS['waybar_config'], waybar_config_temp):
        shutil.copy(waybar_config_temp, CONFIG_PATHS['waybar_config'])
    
    # Waybar style
    waybar_style_temp = TEMP_PATH / "waybar_style"
    if download_file_with_progress(DOWNLOAD_URLS['waybar_style'], waybar_style_temp):
        shutil.copy(waybar_style_temp, CONFIG_PATHS['waybar_style'])
    
    # Rofi config
    rofi_config_temp = TEMP_PATH / "rofi_config"
    if download_file_with_progress(DOWNLOAD_URLS['rofi_config'], rofi_config_temp):
        shutil.copy(rofi_config_temp, CONFIG_PATHS['rofi_config'])
    
    # Фото
    photo_temp = TEMP_PATH / "1.jpg"
    if download_file_with_progress(DOWNLOAD_URLS['sample_photo'], photo_temp):
        shutil.copy(photo_temp, CONFIG_PATHS['photo'])
    
    # Конфиг Alacritty
    alacritty_config = """
[window]
opacity = 0.9
padding.x = 12
padding.y = 12
decorations = "full"
decorations_theme_variant = "dark"  # Для чёрного интерфейса

[font]
size = 14.0

# Используем Fira Code с явным указанием стилей
normal.family = "Fira Code"
bold.family = "Fira Code"
italic.family = "Fira Code"
bold_italic.family = "Fira Code"

# Фикс съезжающих букв:
glyph_offset.y = 1  # Корректировка по вертикали
offset.x = 0
offset.y = 1

[colors]
# Чёрный терминал (инверсия цветов)
primary.foreground = "#ffffff"  # Белый текст
primary.background = "#000000"  # Чёрный фон

# Цвета курсора (инвертированные)
cursor.text = "#000000"  # Чёрный текст под курсором
cursor.cursor = "#ffffff"  # Белый курсор

[colors.normal]
black = "#000000"
white = "#ffffff"

[colors.bright]
black = "#222222"
white = "#eeeeee"
"""
    with open(CONFIG_PATHS['alacritty_config'], 'w') as f:
        f.write(alacritty_config.strip())
    
    # Скрипты Waybar
    print(f"{Colors.OKBLUE}Настройка скриптов Waybar...{Colors.ENDC}")
    setup_waybar_scripts()

def setup_waybar_scripts():
    """Установка скриптов для Waybar в .config/waybar"""
    scripts = {
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
        
        'power-menu.py': """#!/usr/bin/env python3
import subprocess
import json

def get_power_menu():
    return {
        "text": "⏻",
        "tooltip": "Меню питания",
        "class": "power-menu"
    }

print(json.dumps(get_power_menu()))""",
        
        'wifi-quality.py': """#!/usr/bin/env python3
import json
import subprocess

def get_wifi_quality():
    try:
        result = subprocess.run(['iwconfig'], capture_output=True, text=True)
        lines = result.stdout.split('\\n')
        for line in lines:
            if 'Link Quality' in line:
                quality = line.split('Link Quality=')[1].split()[0]
                percent = int(quality.split('/')[0]) / int(quality.split('/')[1]) * 100
                icon = "📶"
                if percent > 75:
                    cls = "good"
                elif percent > 50:
                    cls = "moderate"
                elif percent > 25:
                    cls = "poor"
                else:
                    cls = "bad"
                return {
                    "text": f"{icon} {int(percent)}%",
                    "tooltip": f"Качество Wi-Fi: {int(percent)}%",
                    "class": cls
                }
        return {"text": "⚠️ Offline", "tooltip": "Нет соединения Wi-Fi"}
    except:
        return {"text": "❌ Error", "tooltip": "Ошибка получения качества Wi-Fi"}

print(json.dumps(get_wifi_quality()))"""
    }

    for script_name, script_content in scripts.items():
        script_path = CONFIG_PATHS['waybar_scripts'] / script_name
        with open(script_path, 'w') as f:
            f.write(script_content)
        os.chmod(script_path, 0o755)
    
    # Создаем скрипт для выключения/перезагрузки
    power_script = CONFIG_PATHS['local_bin'] / 'power-menu'
    with open(power_script, 'w') as f:
        f.write("""#!/bin/sh
case "$1" in
    shutdown)
        systemctl poweroff
        ;;
    reboot)
        systemctl reboot
        ;;
    lock)
        swaylock
        ;;
    logout)
        swaymsg exit
        ;;
    *)
        echo "Usage: $0 {shutdown|reboot|lock|logout}"
        exit 1
esac
""")
    os.chmod(power_script, 0o755)

def setup_services():
    """Настройка systemd сервисов"""
    print(f"{Colors.HEADER}Настройка сервисов...{Colors.ENDC}")
    
    # Автозапуск Sway
    xdg_config_dir = HOME / '.config' / 'systemd' / 'user'
    xdg_config_dir.mkdir(parents=True, exist_ok=True)
    
    sway_service = xdg_config_dir / 'sway.service'
    with open(sway_service, 'w') as f:
        f.write(f"""[Unit]
Description=Sway - Wayland window manager
Documentation=man:sway(1)
BindsTo=graphical-session.target

[Service]
Type=simple
ExecStart=/usr/bin/sway
Restart=on-failure
RestartSec=1
TimeoutStopSec=10

[Install]
WantedBy=graphical-session.target
""")
    
    run_cmd("systemctl --user enable sway.service")
    run_cmd("systemctl --user daemon-reload")
    
    # Включение linger для пользователя
    run_cmd(f"sudo loginctl enable-linger {USER}", sudo=True)

def main():
    print(f"{Colors.HEADER}{Colors.BOLD}Полная автоматическая настройка системы{Colors.ENDC}")
    
    # Проверка на root
    if os.geteuid() == 0:
        print(f"{Colors.FAIL}Ошибка: Не запускайте скрипт от root!{Colors.ENDC}")
        sys.exit(1)
    
    try:
        # Установка yay
        install_yay()
        
        # Установка пакетов
        install_packages()
        
        # Установка шрифтов
        install_fonts()
        
        # Настройка конфигураций
        setup_configs()
        
        # Настройка сервисов
        setup_services()
        
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}Настройка успешно завершена!{Colors.ENDC}")
        print(f"\n{Colors.BOLD}Что сделано:{Colors.ENDC}")
        print("- Установлен yay (AUR helper)")
        print("- Установлены все необходимые пакеты через yay")
        print("- Установлены шрифты (Nerd Fonts + Emoji)")
        print("- Настроены конфиги Sway, Waybar, Rofi, Alacritty")
        print("- Установлены скрипты Waybar в ~/.config/waybar")
        print("- Настроен автозапуск Sway через systemd")
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
