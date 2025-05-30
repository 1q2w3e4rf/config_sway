#!/bin/bash
# ======================================================
# Улучшенная конфигурация Bash
# Версия: 0.0.2
# Последнее обновление: 30.05.25
# Автор: 1q2w3e4rf
# GitHub: https://github.com/1q2w3e4rf/config_sway
# ======================================================

# ============ НАСТРОЙКА ПРИГЛАШЕНИЯ ==================
# Цветное приглашение с индикатором статуса выполнения
set_prompt() {
    local EXIT="$?"  # Получаем статус последней команды
    local RED="\[\033[0;31m\]"
    local GREEN="\[\033[0;32m\]"
    local YELLOW="\[\033[0;33m\]"
    local BLUE="\[\033[0;34m\]"
    local PURPLE="\[\033[0;35m\]"
    local CYAN="\[\033[0;36m\]"
    local WHITE="\[\033[0;37m\]"
    local RESET="\[\033[0m\]"

    # Формат приглашения: пользователь@хост путь
    PS1="\n${CYAN}\u${WHITE}@${YELLOW}\h ${GREEN}\w\n"
    
    # Разный цвет стрелки в зависимости от статуса
    if [ $EXIT -eq 0 ]; then
        PS1+="${GREEN}❯${RESET} "  # Зеленая стрелка при успехе
    else
        PS1+="${RED}❯${RESET} "    # Красная стрелка при ошибке
    fi
}
PROMPT_COMMAND='set_prompt'  # Обновлять приглашение после каждой команды

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
# Улучшенная функция edit с автоматическим sudo для системных файлов
edit() {
    local file="$1"
    local needs_sudo=0
    
    # Проверяем, нужно ли sudo для редактирования файла
    if [ -n "$file" ]; then
        if [ ! -w "$file" ] && [ ! -w "$(dirname "$file")" ]; then
            needs_sudo=1
        fi
        
        # Если файл не существует, проверяем права на родительскую директорию
        if [ ! -e "$file" ]; then
            if [ ! -w "$(dirname "$file")" ]; then
                needs_sudo=1
            fi
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

    # Языко-специфичные настройки
    case "$file" in
        *.py)
            echo "Режим Python: используйте TAB для автодополнения"
            $editor -c "set foldmethod=indent" -c "set number" "$file"
            ;;
        *.java)
            echo "Режим Java: доступно автодополнение классов"
            $editor -c "set syntax=java" -c "set number" "$file"
            ;;
        *.c|*.h|*.cpp)
            echo "Режим C/C++: включена подсветка синтаксиса"
            $editor -c "set syntax=cpp" -c "set number" "$file"
            ;;
        *)
            if [ -n "$file" ]; then
                $editor "$file"
            else
                $editor
            fi
            ;;
    esac
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
        echo "$cmd" | xclip -sel clip
        echo "Команда скопирована в буфер: $cmd"
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

# ============ ПРИВЕТСТВЕННОЕ СООБЩЕНИЕ =============
echo -e "\n\033[1;34mИнформация о системе:\033[0m"
echo -e "Имя хоста: \033[1;32m$(hostname)\033[0m"
echo -e "Ядро: \033[1;32m$(uname -r)\033[0m"
echo -e "Время работы: \033[1;32m$(uptime -p)\033[0m"
echo -e "Оболочка: \033[1;32m$(basename $SHELL)\033[0m"
echo -e "\n\033[1;34mСоветы по использованию:\033[0m"
echo -e "Начните вводить команду и нажмите \033[1;33mTab\033[0m для выбора"
echo -e "Используйте \033[1;33mhist\033[0m для поиска по истории команд"
echo -e "Используйте \033[1;33mvf\033[0m для быстрого редактирования файлов"
echo -e "Используйте \033[1;33mCtrl+R\033[0m для поиска по истории"
echo -e "Используйте \033[1;33medit file\033[0m для редактирования файлов (автоматический sudo)"
