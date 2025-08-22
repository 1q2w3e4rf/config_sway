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

USER = os.getenv('USER')
HOME = Path.home()
TEMP_DIR = TemporaryDirectory()
TEMP_PATH = Path(TEMP_DIR.name)

CONFIG_PATHS = {
    'sway_config': HOME / '.config' / 'sway' / 'config',
    'waybar_config': HOME / '.config' / 'waybar' / 'config.jsonc',
    'waybar_style': HOME / '.config' / 'waybar' / 'style.css',
    'waybar_scripts': HOME / '.config' / 'waybar',
    'photo': HOME / 'photo' / '1.jpg',
    'local_bin': HOME / '.local' / 'bin',
    'fonts_dir': HOME / '.local' / 'share' / 'fonts',
    'rofi_config': HOME / '.config' / 'rofi' / 'config.rasi',
    'alacritty_config': HOME / '.config' / 'alacritty' / 'alacritty.toml',
    'swaync_config': HOME / '.config' / 'swaync' / 'config.json',
    'swaync_style': HOME / '.config' / 'swaync' / 'style.css'
}

DOWNLOAD_URLS = {
    'nerd_fonts': "https://github.com/ryanoasis/nerd-fonts/releases/download/v3.0.2/JetBrainsMono.zip",
    'noto_emoji': "https://github.com/googlefonts/noto-emoji/raw/main/fonts/NotoColorEmoji.ttf",
    'sway_config': "https://raw.githubusercontent.com/1q2w3e4rf/config_sway/main/config",
    'waybar_config': "https://raw.githubusercontent.com/1q2w3e4rf/config_sway/main/config.jsonc",
    'waybar_style': "https://raw.githubusercontent.com/1q2w3e4rf/config_sway/main/style.css",
    'sample_photo': "https://github.com/1q2w3e4rf/config_sway/raw/main/1.jpg",
    'rofi_config': "https://raw.githubusercontent.com/1q2w3e4rf/config_sway/main/config.rasi",
    'swaync_config': "https://raw.githubusercontent.com/1q2w3e4rf/config_sway/main/swaync_config.json",
    'swaync_style': "https://raw.githubusercontent.com/1q2w3e4rf/config_sway/main/swaync_style.css"
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
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"

def run_cmd(cmd, sudo=False, password=None):
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
                        if now - last_print >= 1.0:
                            elapsed = now - start_time
                            speed = downloaded / elapsed if elapsed > 0 else 0
                            remaining = (total_size - downloaded) / speed if speed > 0 else 0
                            
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
            
            print()
            return True
            
    except requests.exceptions.RequestException as e:
        print(f"\n{Colors.FAIL}Ошибка при загрузке: {e}{Colors.ENDC}")
        return False
    except Exception as e:
        print(f"\n{Colors.FAIL}Неизвестная ошибка: {e}{Colors.ENDC}")
        return False

def install_yay():
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
    print(f"{Colors.HEADER}Установка пакетов...{Colors.ENDC}")
    
    packages = [
        'sway', 'swaybg', 'swayidle', 'swaylock', 'swaync',
        'waybar', 'gtk-layer-shell', 'libdbusmenu-gtk3',
        'alacritty', 'rofi', 'wofi', 'wlogout',
        'ttf-jetbrains-mono-nerd', 'noto-fonts-emoji', 'ttf-font-awesome',
        'nerd-fonts-complete', 'adwaita-icon-theme',
        'pulseaudio', 'pulseaudio-alsa', 'pulseaudio-bluetooth',
        'pavucontrol', 'pamixer', 'wireplumber', 'playerctl', 'libpulse',
        'networkmanager', 'network-manager-applet', 'wireless_tools', 'iwd',
        'blueman', 'bluez', 'bluez-utils', 'brightnessctl', 'light', 'upower',
        'polkit-gnome', 'gnome-keyring', 'libnotify', 'dunst', 'grim', 'slurp',
        'wf-recorder', 'wl-clipboard', 'clipman', 'python', 'python-pip',
        'python-dbus-next', 'python-requests', 'python-gobject', 'python-i3ipc',
        'qt5-wayland', 'qt6-wayland', 'xdg-desktop-portal-wlr', 'gtk3',
        'gtk-engine-murrine', 'mesa', 'glu', 'vulkan-radeon', 'jq', 'htop',
        'curl', 'imv', 'zathura', 'zathura-pdf-mupdf', 'nmtui', 'nwg-look-bin',
        'wireguard-tools', 'openvpn', 'jsoncpp', 'libmpdclient', 'libnl',
        'libepoxy', 'scdoc'
    ]

    if not run_cmd(f"yay -S --needed --noconfirm {' '.join(packages)}"):
        print(f"{Colors.WARNING}Попробуем установить пакеты по одному...{Colors.ENDC}")
        for pkg in packages:
            if not run_cmd(f"yay -S --needed --noconfirm {pkg}"):
                print(f"{Colors.FAIL}Не удалось установить {pkg}{Colors.ENDC}")

def install_fonts():
    print(f"{Colors.HEADER}Установка шрифтов...{Colors.ENDC}")
    
    os.makedirs(CONFIG_PATHS['fonts_dir'], exist_ok=True)
    
    nerd_zip = TEMP_PATH / "nerd_fonts.zip"
    if download_file_with_progress(DOWNLOAD_URLS['nerd_fonts'], nerd_zip):
        with zipfile.ZipFile(nerd_zip, 'r') as zip_ref:
            zip_ref.extractall(CONFIG_PATHS['fonts_dir'])
    
    emoji_font = TEMP_PATH / "NotoColorEmoji.ttf"
    if download_file_with_progress(DOWNLOAD_URLS['noto_emoji'], emoji_font):
        shutil.copy(emoji_font, CONFIG_PATHS['fonts_dir'])
    
    run_cmd("fc-cache -fv")

def setup_configs():
    print(f"{Colors.HEADER}Настройка конфигураций...{Colors.ENDC}")
    
    os.makedirs(HOME / '.config' / 'sway', exist_ok=True)
    os.makedirs(HOME / '.config' / 'waybar', exist_ok=True)
    os.makedirs(HOME / '.config' / 'rofi', exist_ok=True)
    os.makedirs(HOME / '.config' / 'alacritty', exist_ok=True)
    os.makedirs(HOME / '.config' / 'swaync', exist_ok=True)
    os.makedirs(HOME / 'photo', exist_ok=True)
    os.makedirs(CONFIG_PATHS['local_bin'], exist_ok=True)
    
    print(f"{Colors.OKBLUE}Загрузка конфигураций...{Colors.ENDC}")
    
    sway_config_temp = TEMP_PATH / "sway_config"
    if download_file_with_progress(DOWNLOAD_URLS['sway_config'], sway_config_temp):
        shutil.copy(sway_config_temp, CONFIG_PATHS['sway_config'])
    
    waybar_config_temp = TEMP_PATH / "waybar_config"
    if download_file_with_progress(DOWNLOAD_URLS['waybar_config'], waybar_config_temp):
        shutil.copy(waybar_config_temp, CONFIG_PATHS['waybar_config'])
    
    waybar_style_temp = TEMP_PATH / "waybar_style"
    if download_file_with_progress(DOWNLOAD_URLS['waybar_style'], waybar_style_temp):
        shutil.copy(waybar_style_temp, CONFIG_PATHS['waybar_style'])
    
    rofi_config_temp = TEMP_PATH / "rofi_config"
    if download_file_with_progress(DOWNLOAD_URLS['rofi_config'], rofi_config_temp):
        shutil.copy(rofi_config_temp, CONFIG_PATHS['rofi_config'])
    
    photo_temp = TEMP_PATH / "1.jpg"
    if download_file_with_progress(DOWNLOAD_URLS['sample_photo'], photo_temp):
        shutil.copy(photo_temp, CONFIG_PATHS['photo'])
    
    swaync_config_temp = TEMP_PATH / "swaync_config"
    if download_file_with_progress(DOWNLOAD_URLS['swaync_config'], swaync_config_temp):
        shutil.copy(swaync_config_temp, CONFIG_PATHS['swaync_config'])
    
    swaync_style_temp = TEMP_PATH / "swaync_style"
    if download_file_with_progress(DOWNLOAD_URLS['swaync_style'], swaync_style_temp):
        shutil.copy(swaync_style_temp, CONFIG_PATHS['swaync_style'])
    
    alacritty_config = """
[window]
opacity = 0.9
padding.x = 12
padding.y = 12
decorations = "full"
decorations_theme_variant = "dark"

[font]
size = 14.0
normal.family = "Fira Code"
bold.family = "Fira Code"
italic.family = "Fira Code"
bold_italic.family = "Fira Code"
glyph_offset.y = 1
offset.x = 0
offset.y = 1

[colors]
primary.foreground = "#ffffff"
primary.background = "#000000"
cursor.text = "#000000"
cursor.cursor = "#ffffff"

[colors.normal]
black = "#000000"
white = "#ffffff"

[colors.bright]
black = "#222222"
white = "#eeeeee"
"""
    with open(CONFIG_PATHS['alacritty_config'], 'w') as f:
        f.write(alacritty_config.strip())
    
    print(f"{Colors.OKBLUE}Настройка скриптов Waybar...{Colors.ENDC}")
    setup_waybar_scripts()

def setup_waybar_scripts():
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

print(json.dumps(get_lang()))"""
    }

    for script_name, script_content in scripts.items():
        script_path = CONFIG_PATHS['waybar_scripts'] / script_name
        with open(script_path, 'w') as f:
            f.write(script_content)
        os.chmod(script_path, 0o755)
    
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
    print(f"{Colors.HEADER}Настройка сервисов...{Colors.ENDC}")
    
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
    
    run_cmd(f"sudo loginctl enable-linger {USER}", sudo=True)

def main():
    print(f"{Colors.HEADER}{Colors.BOLD}Полная автоматическая настройка системы{Colors.ENDC}")
    
    if os.geteuid() == 0:
        print(f"{Colors.FAIL}Ошибка: Не запускайте скрипт от root!{Colors.ENDC}")
        sys.exit(1)
    
    try:
        install_yay()
        install_packages()
        install_fonts()
        setup_configs()
        setup_services()
        
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}Настройка успешно завершена!{Colors.ENDC}")
        print(f"\n{Colors.BOLD}Что сделано:{Colors.ENDC}")
        print("- Установлен yay (AUR helper)")
        print("- Установлены все необходимые пакеты через yay")
        print("- Установлены шрифты (Nerd Fonts + Emoji)")
        print("- Настроены конфиги Sway, Waybar, Rofi, Alacritty, SwayNC")
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
