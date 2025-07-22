#!/usr/bin/env python3
import os
import subprocess
import shutil
import sys
from pathlib import Path

def run_command(cmd, sudo=False):
    """Выполняет команду в shell с возможностью sudo"""
    if sudo:
        cmd = ["sudo"] + cmd
    print(f"Выполняю: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

def check_install(package):
    """Проверяет установлен ли пакет"""
    try:
        subprocess.run(["pacman", "-Qi", package], check=True, 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def install_packages():
    """Устанавливает необходимые пакеты"""
    packages = [
        "sway",
        "waybar",
        "rofi",
        "grim",
        "slurp",
        "alacritty",
        "dolphin",
        "yandex-browser-stable",
        "steam",
        "light",
        "pulseaudio",
        "pavucontrol",
        "networkmanager",
        "swaylock",
        "swayidle",
        "swaybg",
        "ttf-jetbrains-mono-nerd",
        "noto-fonts-emoji",
        "python-i3ipc"  # Для скриптов Waybar
    ]
    
    # Проверяем Sway
    if not check_install("sway"):
        print("\nУстановка Sway и зависимостей...")
        run_command(["pacman", "-S", "--needed", "--noconfirm"] + packages, sudo=True)
    else:
        print("Sway уже установлен, пропускаем установку пакетов")

def setup_configs(repo_path):
    """Настраивает конфигурационные файлы"""
    home = Path.home()
    
    # 1. Настройка Sway
    print("\nНастраиваю Sway...")
    sway_config_dir = home / ".config" / "sway"
    sway_config_dir.mkdir(parents=True, exist_ok=True)
    
    # Копируем основной конфиг
    shutil.copy(repo_path / "config", sway_config_dir / "config")
    
    # Копируем скрипт для управления подсветкой
    backlight_script = sway_config_dir / "backlight.sh"
    if not backlight_script.exists():
        with open(backlight_script, "w") as f:
            f.write("""#!/bin/sh
            # Скрипт управления подсветкой
            case $1 in
                -inc) light -A $2;;
                -dec) light -U $2;;
            esac
            """)
        backlight_script.chmod(0o755)
    
    # 2. Настройка Waybar
    print("Настраиваю Waybar...")
    waybar_config_dir = home / ".config" / "waybar"
    waybar_config_dir.mkdir(parents=True, exist_ok=True)
    
    # Копируем конфигурационные файлы
    shutil.copy(repo_path / "style.css", waybar_config_dir / "style.css")
    shutil.copy(repo_path / "config.jsonc", waybar_config_dir / "config")
    
    # 3. Копируем обои
    print("Копирую обои...")
    wallpapers_dir = home / "photo"
    wallpapers_dir.mkdir(exist_ok=True)
    
    for img in (repo_path / "photo").glob("*"):
        shutil.copy(img, wallpapers_dir)
    
    # 4. Настройка шрифтов
    print("Настраиваю шрифты...")
    font_dir = home / ".local" / "share" / "fonts"
    font_dir.mkdir(parents=True, exist_ok=True)
    
    # Копируем дополнительные шрифты если есть
    if (repo_path / "fonts").exists():
        for font in (repo_path / "fonts").glob("*"):
            shutil.copy(font, font_dir)
        
        # Обновляем кэш шрифтов
        run_command(["fc-cache", "-fv"])

def main():
    # Проверяем права root
    if os.geteuid() != 0:
        print("Запустите скрипт с sudo для установки пакетов")
        sys.exit(1)
    
    # Получаем путь к репозиторию (где находится этот скрипт)
    repo_path = Path(__file__).parent.resolve()
    
    print(f"Установка конфигурации из: {repo_path}")
    print("Этот скрипт установит Sway, Waybar и настроит окружение")
    
    # 1. Установка пакетов
    install_packages()
    
    # 2. Настройка конфигов
    setup_configs(repo_path)
    
    # 3. Завершение
    print("\nУстановка завершена успешно!")
    print("Для запуска Sway выполните:")
    print("  sway")
    print("Или перезагрузите систему")

if __name__ == "__main__":
    main()