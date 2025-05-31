#!/bin/bash
# ======================================================
# Улучшенная конфигурация Bash
# Версия: 0.0.8
# Последнее обновление: 30.05.25
# Автор: 1q2w3e4rf
# GitHub: https://github.com/1q2w3e4rf/config_sway
# ======================================================

# ============ ИНФОРМАЦИЯ О СИСТЕМЕ ==================
_system_info() {
    echo -e "\n\033[1;34m╔════════════════════════════════════════╗"
    echo -e "║             СИСТЕМНАЯ ИНФОРМАЦИЯ            ║"
    echo -e "╚════════════════════════════════════════╝\033[0m"
    
    # Основная информация
    echo -e "\n\033[1;32m● Основное:\033[0m"
    echo -e "  \033[1;33m├─ Хост:\033[0m $(hostname 2>/dev/null || echo "неизвестно")"
    echo -e "  \033[1;33m├─ Пользователь:\033[0m $(whoami)"
    echo -e "  \033[1;33m└─ Оболочка:\033[0m $(basename "$SHELL")"
    
    # Информация об ОС
    echo -e "\n\033[1;32m● Операционная система:\033[0m"
    if [ -f /etc/os-release ]; then
        source /etc/os-release
        echo -e "  \033[1;33m├─ Дистрибутив:\033[0m ${PRETTY_NAME:-неизвестно}"
        echo -e "  \033[1;33m└─ Версия:\033[0m ${VERSION_ID:-неизвестно}"
    elif command -v lsb_release &>/dev/null; then
        echo -e "  \033[1;33m└─ Дистрибутив:\033[0m $(lsb_release -ds 2>/dev/null)"
    else
        echo -e "  \033[1;33m└─ Дистрибутив:\033[0m неизвестно"
    fi
    
    # Информация о ядре
    echo -e "\n\033[1;32m● Ядро:\033[0m"
    echo -e "  \033[1;33m├─ Версия:\033[0m $(uname -r 2>/dev/null)"
    echo -e "  \033[1;33m└─ Архитектура:\033[0m $(uname -m 2>/dev/null)"
    
    # Аптайм и память
    echo -e "\n\033[1;32m● Ресурсы:\033[0m"
    echo -e "  \033[1;33m├─ Аптайм:\033[0m $(uptime -p 2>/dev/null | sed 's/up //' || echo "неизвестно")"
    echo -e "  \033[1;33m├─ Память:\033[0m $(free -h 2>/dev/null | awk '/Mem/{print $3"/"$2}' || echo "неизвестно") (используется/всего)"
    echo -e "  \033[1;33m└─ Загрузка CPU:\033[0m $(uptime 2>/dev/null | awk -F 'load average: ' '{print $2}' || echo "неизвестно")"
    
    # Диски
    echo -e "\n\033[1;32m● Дисковое пространство:\033[0m"
    df -h 2>/dev/null | grep -v "tmpfs" | awk '{printf "  \033[1;33m├─ %-15s %-10s %-10s %-10s\033[0m\n", $1, $3, $5, $6}' | head -n 4
    df -h 2>/dev/null | grep -v "tmpfs" | awk 'NR>4 {printf "  \033[1;33m└─ %-15s %-10s %-10s %-10s\033[0m\n", $1, $3, $5, $6}' | tail -n 1
    
    # Сетевые интерфейсы
    echo -e "\n\033[1;32m● Сетевые интерфейсы:\033[0m"
    ip -o -4 addr show 2>/dev/null | awk '{print $2": "$4}' | while read -r line; do
        echo -e "  \033[1;33m├─ $line\033[0m"
    done | head -n 2
    ip -o -4 addr show 2>/dev/null | awk '{print $2": "$4}' | while read -r line; do
        echo -e "  \033[1;33m└─ $line\033[0m"
    done | tail -n 1
    
    # Температура (если доступно)
    if [ -f /sys/class/thermal/thermal_zone0/temp ]; then
        temp=$(($(cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null)/1000))
        echo -e "\n\033[1;32m● Температура CPU:\033[0m \033[1;33m${temp:-неизвестно}°C\033[0m"
    fi
    
    # Советы по использованию
    echo -e "\n\033[1;34m╔════════════════════════════════════════╗"
    echo -e "║             СОВЕТЫ ПО ИСПОЛЬЗОВАНИЮ          ║"
    echo -e "╚════════════════════════════════════════╝\033[0m"
    echo -e "  \033[1;33m• Начните вводить команду и нажмите Tab для выбора\033[0m"
    echo -e "  \033[1;33m• Используйте hist для поиска по истории команд\033[0m"
    echo -e "  \033[1;33m• Используйте vf для быстрого редактирования файлов\033[0m"
    echo -e "  \033[1;33m• Используйте se <термин> для поиска в файлах\033[0m"
    echo -e "  \033[1;33m• Используйте Ctrl+R для поиска по истории\033[0m"
    echo -e "  \033[1;33m• Используйте edit file для редактирования (авто sudo)\033[0m"
    echo -e "  \033[1;33m• Используйте update для обновления системы\033[0m"
    echo -e "  \033[1;33m• Используйте cleanup для очистки системы\033[0m"
}

case $- in
    *i*) _system_info ;;
esac

# ============ НАСТРОЙКА ПРИГЛАШЕНИЯ ==================
set_prompt() {
    local EXIT="$?"
    local RED="\[\033[0;31m\]"
    local GREEN="\[\033[0;32m\]"
    local YELLOW="\[\033[0;33m\]"
    local CYAN="\[\033[0;36m\]"
    local WHITE="\[\033[0;37m\]"
    local RESET="\[\033[0m\]"

    PS1="\n${CYAN}\u${WHITE}@${YELLOW}\h ${GREEN}\w\n"
    [ $EXIT -eq 0 ] && PS1+="${GREEN}❯${RESET} " || PS1+="${RED}❯${RESET} "
}
PROMPT_COMMAND='set_prompt'

# ========== УМНОЕ АВТОДОПОЛНЕНИЕ ====================
# Автодополнение на основе fzf для команд и истории
if ! command -v fzf &>/dev/null; then
    echo "Для умного автодополнения установите fzf:"
    echo "sudo pacman -S fzf"
fi

_custom_complete() {
    local cur prev words cword
    _init_completion || return

    # Получаем список команд из PATH и истории
    local commands=$(compgen -c | sort -u)
    local history_commands=$(history | awk '{$1=""; print $0}' | sort -u)
    local all_suggestions=$(echo -e "$commands\n$history_commands" | grep -v '^$' | sort -u)

    # Фильтруем по текущему вводу
    local suggestions=$(echo "$all_suggestions" | grep -i "^$cur")

    # Показываем интерактивное меню при нескольких вариантах
    if [ $(echo "$suggestions" | wc -l) -gt 1 ]; then
        local selected=$(echo "$suggestions" | fzf --height 40% --reverse \
            --prompt="Выберите команду: " --preview 'whatis {} 2>/dev/null || echo "Нет описания"')
        if [ -n "$selected" ]; then
            COMPREPLY=("$selected")
            return
        fi
    fi

    COMPREPLY=($(compgen -c "$cur"))
}

complete -F _custom_complete -o default -o bashdefault

# Настройки интерактивного автодополнения
bind 'TAB:menu-complete'               # Циклическое переключение вариантов
bind 'set show-all-if-ambiguous on'    # Показывать все варианты
bind 'set menu-complete-display-prefix on'  # Показывать префикс
bind 'set completion-ignore-case on'   # Игнорировать регистр
bind '"\e[A": history-search-backward' # Поиск в истории стрелкой вверх
bind '"\e[B": history-search-forward'  # Поиск в истории стрелкой вниз

# ===== АВТОДОПОЛНЕНИЕ ДЛЯ КОНКРЕТНЫХ КОМАНД =========
# Автодополнение для pacman/yay
_pacman_complete() {
    local cur prev words cword
    _init_completion || return
    
    if [[ $prev == "-S" || $prev == "--sync" || $prev == "-R" || $prev == "--remove" ]]; then
        COMPREPLY=($(pacman -Ssq "$cur" 2>/dev/null | fzf --height 40% --reverse \
            --multi --prompt="Выберите пакет(ы): "))
    else
        COMPREPLY=($(compgen -W "-S -R -Qs -Qi -Ql -Qo -F -U --sync --remove --search \
            --info --list --owns --file --upgrade" -- "$cur"))
    fi
}
complete -F _pacman_complete pacman yay

# Автодополнение для Python модулей
_python_complete() {
    local cur prev words cword
    _init_completion || return
    
    if [[ $prev == "-m" ]]; then
        COMPREPLY=($(python -c "import pkgutil; print('\n'.join([pkg[1] for pkg in pkgutil.iter_modules()]))" 2>/dev/null | 
                   fzf --height 40% --reverse --prompt="Выберите модуль: "))
    fi
}
complete -F _python_complete python python3

# Автодополнение для Git (если установлен)
if command -v git &>/dev/null; then
    _git_complete() {
        local cur prev words cword
        _init_completion || return
        
        if [[ $prev == "git" ]]; then
            COMPREPLY=($(compgen -W "$(git help -a | grep '^  [a-z]' | awk '{print $1}')" -- "$cur" | 
                         fzf --height 40% --reverse --prompt="Выберите git команду: "))
        fi
    }
    complete -F _git_complete git
fi

# ============ УЛУЧШЕННЫЕ АЛИАСЫ LS =================
# Современные аналоги стандартных команд
if command -v exa &>/dev/null; then
    alias ls='exa --group-directories-first'  # Улучшенный ls
    alias ll='exa -lh --group-directories-first --color=never --time-style=long-iso'
    alias la='exa -a --group-directories-first'
    alias lla='exa -lha --group-directories-first --color=never --time-style=long-iso'
else
    alias ls='ls --color=auto --group-directories-first'
    alias ll='ls -lh --color=auto --group-directories-first'
    alias la='ls -a --color=auto --group-directories-first'
    alias lla='ls -lha --color=auto --group-directories-first'
fi

# ============ УМНЫЙ РЕДАКТОР =======================
# Улучшенная функция edit с автоматическим sudo и поиском
edit() {
    local file="$1"
    local search_term="$2"
    local needs_sudo=0
    
    # Проверяем, нужно ли sudo для редактирования файла
    if [ -n "$file" ]; then
        if { [ -e "$file" ] && [ ! -w "$file" ]; } || 
           { [ ! -e "$file" ] && [ ! -w "$(dirname "$file")" ]; }; then
            needs_sudo=1
        fi
    fi

    # Выбираем лучший доступный редактор
    local editor=""
    if command -v nvim &>/dev/null; then
        editor="nvim"
    elif command -v vim &>/dev/null; then
        editor="vim"
    else
        editor="nano"
    fi

    # Добавляем sudo если нужно
    if [ $needs_sudo -eq 1 ]; then
        editor="sudo $editor"
    fi

    # Подготовка команды с поиском (если указан термин)
    local edit_cmd="$editor"
    if [ -n "$search_term" ]; then
        case "$editor" in
            *nvim*) edit_cmd+=" -c \"/$search_term\"" ;;
            *vim*)  edit_cmd+=" -c \"/$search_term\"" ;;
            *nano*) edit_cmd+=" --afterends \"$search_term\"" ;;
        esac
    fi

    # Языко-специфичные настройки
    case "$file" in
        *.py)
            echo "Режим Python: используйте TAB для автодополнения"
            edit_cmd+=" -c \"set foldmethod=indent\" -c \"set number\""
            ;;
        *.java)
            echo "Режим Java: доступно автодополнение классов"
            edit_cmd+=" -c \"set syntax=java\" -c \"set number\""
            ;;
        *.c|*.h|*.cpp)
            echo "Режим C/C++: включена подсветка синтаксиса"
            edit_cmd+=" -c \"set syntax=cpp\" -c \"set number\""
            ;;
        *)
            [ -n "$file" ] && edit_cmd+=" -c \"set number\""
            ;;
    esac

    # Добавляем файл и выполняем команду
    [ -n "$file" ] && edit_cmd+=" \"$file\""
    eval "$edit_cmd"
}

# ============ ПОИСК В ФАЙЛАХ ========================
# Поиск с fzf и открытие в редакторе с подсветкой
search_and_edit() {
    local search_term=$1
    if [ -z "$search_term" ]; then
        echo "Использование: search_and_edit <термин>"
        return 1
    fi

    local selected_file=$(grep -rl "$search_term" . 2>/dev/null | \
        fzf --height 40% --reverse --preview "grep -n --color=always '$search_term' {}")
    
    [ -n "$selected_file" ] && edit "$selected_file" "$search_term"
}

# ============ ПОЛЕЗНЫЕ АЛИАСЫ ======================
# Улучшенные версии стандартных команд
alias grep='grep --color=auto'
alias diff='diff --color=auto'
alias ip='ip -color=auto'
alias pacman='sudo pacman --color=auto'
alias yay='yay --color=auto'
alias vim='nvim'
alias top='btm'      # Современная замена top
alias du='dust'      # Улучшенный du
alias df='duf'       # Улучшенный df
alias ps='procs'     # Улучшенный ps
alias sudo='sudo '   # Пробел позволяет алиасам работать с sudo

# Полезные сокращения
alias please='sudo $(history -p !!)'  # Повторить последнюю команду с sudo
alias fuck='eval $(thefuck $(fc -ln -1)); history -r'  # Исправление ошибок
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'
alias .....='cd ../../../..'
alias c='clear'      # Очистка экрана
alias h='tldr'       # Краткая справка по командам
alias update='sudo pacman -Syu && yay -Syu'  # Обновление системы
alias cleanup='sudo pacman -Rns $(pacman -Qtdq)'  # Очистка системы
alias se='search_and_edit'  # Поиск в файлах

# ============ ПОЛЕЗНЫЕ ФУНКЦИИ =====================
# Создать директорию и перейти в нее
mkcd() { mkdir -p "$1" && cd "$1"; }

# Умное извлечение архивов
extract() {
    if [ -f "$1" ]; then
        case "$1" in
            *.tar.bz2) tar xjf "$1" ;;
            *.tar.gz) tar xzf "$1" ;;
            *.bz2) bunzip2 "$1" ;;
            *.rar) unrar x "$1" ;;
            *.gz) gunzip "$1" ;;
            *.tar) tar xf "$1" ;;
            *.tbz2) tar xjf "$1" ;;
            *.tgz) tar xzf "$1" ;;
            *.zip) unzip "$1" ;;
            *.Z) uncompress "$1" ;;
            *.7z) 7z x "$1" ;;
            *) echo "'$1' - неизвестный формат архива" ;;
        esac
    else
        echo "'$1' - файл не существует"
    fi
}

# Поиск по истории команд
hist() {
    local cmd=$(history | fzf --height 40% --reverse --prompt="История команд: " | awk '{$1=""; print substr($0,2)}')
    if [ -n "$cmd" ]; then
        if command -v xclip &>/dev/null; then
            echo "$cmd" | xclip -sel clip
            echo "Команда скопирована в буфер: $cmd"
        else
            echo "Доступная команда: $cmd"
        fi
    fi
}

# Быстрое редактирование файла с автоматическим sudo
vf() {
    local file
    file=$(fzf --height 40% --reverse --preview 'bat --color=always --style=numbers {} 2>/dev/null || echo "Не удалось прочитать файл"')
    
    if [ -n "$file" ]; then
        if [ -w "$file" ] || [ -w "$(dirname "$file")" ]; then
            nvim "$file"
        else
            sudo nvim "$file"
        fi
    fi
}

# ========= НАСТРОЙКИ ИСТОРИИ =======================
HISTCONTROL=ignoreboth  # Игнорировать дубликаты и команды с пробелом
HISTSIZE=5000           # Размер истории в памяти
HISTFILESIZE=10000      # Размер файла истории
shopt -s histappend     # Добавлять в историю, а не перезаписывать
shopt -s cmdhist        # Сохранять многострочные команды как одну
shopt -s lithist        # Сохранять переносы строк в истории

# ========= ДОПОЛНИТЕЛЬНЫЕ НАСТРОЙКИ ================
shopt -s checkwinsize   # Проверять размер окна после каждой команды
shopt -s globstar       # Рекурсивное сопоставление путей **
shopt -s dotglob        # Включать скрытые файлы в подстановки
shopt -s nocaseglob     # Игнорировать регистр при подстановке

# ============ FZF НАСТРОЙКИ ========================
[ -f ~/.fzf.bash ] && source ~/.fzf.bash
