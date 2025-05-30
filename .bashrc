#!/bin/bash
# =============================================
# МОЙ КРУТОЙ BASHRC ДЛЯ SWAY WM
# Настроено для максимального комфорта в работе
# Автор: 1q2w3e4rf
# Последнее обновление: 30.05.2025
# =============================================

# ██████╗  █████╗ ███████╗██╗  ██╗██████╗  ██████╗
# ██╔══██╗██╔══██╗██╔════╝██║  ██║██╔══██╗██╔════╝
# ██████╔╝███████║███████╗███████║██████╔╝██║     
# ██╔══██╗██╔══██║╚════██║██╔══██║██╔══██╗██║     
# ██║  ██║██║  ██║███████║██║  ██║██║  ██║╚██████╗
# ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝

# 🔧 Основные настройки
export EDITOR=nvim               # Люблю Vim :)
export TERMINAL=konsole          # Терминал по умолчанию
export BROWSER=yandex-browser    # Мой любимый браузер

# 🔄 Автодополнение
if [ -f /usr/share/bash-completion/bash_completion ]; then
    source /usr/share/bash-completion/bash_completion
fi

# ========================
# 🎨 НАСТРОЙКА ПРОМПТА
# ========================
set_prompt() {
    local EXIT=$?
    local COL_USER="\[\033[1;32m\]"   # Зеленый - пользователь
    local COL_HOST="\[\033[1;33m\]"   # Желтый - хост
    local COL_DIR="\[\033[1;34m\]"    # Синий - директория
    local COL_RESET="\[\033[0m\]"     # Сброс цвета
    
    PS1="\n${COL_USER}\u${COL_RESET}@${COL_HOST}\h ${COL_DIR}\w\n"
    
    # Красная стрелка если последняя команда упала
    if [ $EXIT -ne 0 ]; then
        PS1+="\[\033[1;31m\]❯${COL_RESET} "
    else
        PS1+="\[\033[1;32m\]❯${COL_RESET} "
    fi
}
PROMPT_COMMAND='set_prompt'

# ========================
# 🚀 АЛИАСЫ И ФУНКЦИИ
# ========================

# 📁 Файловые операции
alias ls='exa --group-directories-first'
alias ll='exa -lh --git --icons'
alias la='exa -a'
alias lla='exa -lha --git --icons'
alias rm='rm -i'                  # Защита от дурака
alias cp='cp -i'
alias mv='mv -i'

# 🖥 Системные команды
alias update='sudo pacman -Syu && yay -Syu'    # Обновить всё
alias clean='sudo pacman -Rns $(pacman -Qtdq)' # Очистка системы
alias reboot='systemctl reboot'
alias off='systemctl poweroff'

# 🎛 Sway WM специфичные
alias sway-reload='swaymsg reload'             # Перезагрузить Sway
alias sway-restart='systemctl --user restart sway' # Перезапустить Sway
alias screenshot='grim -g "$(slurp)" ~/Pictures/Screenshots/$(date +"%Y-%m-%d_%H-%M-%S").png' # Скриншот области

# 🛠 Полезные функции
mkcd() { mkdir -p "$1" && cd "$1"; }  # Создать папку и перейти в неё

# Извлечение архивов
extract() {
    if [ -f "$1" ]; then
        case "$1" in
            *.tar.bz2) tar xjf "$1" ;;
            *.tar.gz)  tar xzf "$1" ;;
            *.zip)     unzip "$1" ;;
            *)         echo "Неизвестный формат архива" ;;
        esac
    else
        echo "Файл не существует: $1"
    fi
}

# ========================
# 🎛 ИНТЕГРАЦИЯ СО SWAY
# ========================

# Установка переменных для правильной работы в Wayland
export QT_QPA_PLATFORM=wayland
export GDK_BACKEND=wayland
export SDL_VIDEODRIVER=wayland
export CLUTTER_BACKEND=wayland
export MOZ_ENABLE_WAYLAND=1

# Функция для запуска GUI приложений в Sway
gui() {
    if [ -z "$WAYLAND_DISPLAY" ]; then
        echo "Не работает в Sway! Запустите из сессии Wayland"
        return 1
    fi
    
    case "$1" in
        browser)  yandex-browser --enable-features=UseOzonePlatform --ozone-platform=wayland ;;
        mail)     thunderbird ;;
        office)   onlyoffice-desktopeditors ;;
        *)        echo "Неизвестное приложение" ;;
    esac
}

# ========================
# ⚙️ НАСТРОЙКА СИСТЕМЫ
# ========================

# История команд
HISTSIZE=5000
HISTFILESIZE=10000
HISTCONTROL=ignoreboth  # Игнорировать дубли и команды с пробелом
shopt -s histappend     # Добавлять в историю, а не перезаписывать

# Удобная навигация
shopt -s autocd         # Переход в папку без cd
shopt -s globstar       # Рекурсивный поиск **
shopt -s nocaseglob     # Игнорирование регистра

# ========================
# 🏁 ЗАПУСК ПРИ СТАРТЕ
# ========================

# Приветственное сообщение
echo -e "\n\033[1;34mДобро пожаловать в \033[1;35mSway WM\033[0m"
echo -e "Терминал: \033[1;32m$TERMINAL\033[0m"
echo -e "Редактор: \033[1;33m$EDITOR\033[0m"
echo -e "Браузер: \033[1;36m$BROWSER\033[0m"
echo -e "\nДоступные команды:"
echo -e "  \033[1;37mupdate\033[0m - Обновить систему"
echo -e "  \033[1;37msway-reload\033[0m - Перезагрузить Sway"
echo -e "  \033[1;37mscreenshot\033[0m - Сделать скриншот области\n"
