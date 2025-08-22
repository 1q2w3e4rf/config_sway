# 🖥️ Sway Configuration Suite

Полная конфигурация для современного Wayland-окружения на основе Sway с кастомизированной панелью Waybar и автоматическим установщиком.

## 📋 Содержание

- [✨ Особенности](#-особенности)
- [🚀 Быстрая установка](#-быстрая-установка)
- [⚙️ Ручная установка](#-ручная-установка)
- [🎛️ Настройка Waybar](#-настройка-waybar)
- [⌨️ Горячие клавиши](#-горячие-клавиши)
- [🎨 Кастомизация](#-кастомизация)
- [🔧 Устранение неполадок](#-устранение-неполадок)
- [📦 Структура проекта](#-структура-проекта)
- [📜 Лицензия](#-лицензия)

## ✨ Особенности

### 🖼️ **Композитор Sway**
- Нативный Wayland-композитор с поддержкой Vim-навигации
- Полная поддержка горячих клавиш в стиле i3wm
- Гладкая анимация и рендеринг
- Поддержка современных протоколов (XDG, Layer Shell)

### 🎛️ **Панель Waybar**
- **Модуль рабочих пространств** с иконками и подсветкой
- **Системные метрики**: CPU, RAM, температура
- **Медиа-контроллер** (поддержка Spotify, MPV, VLC)
- **Погодный модуль** с данными от wttr.in
- **Индикатор раскладки клавиатуры** (рус/англ)
- **Управление звуком** через PulseAudio
- **Сетевой статус** (Wi-Fi/Ethernet)
- **Стильные уведомления** через SwayNC

### 🎨 **Визуальный стиль**
- Цветовая схема **Catppuccin Macchiato**
- Темная тема с акцентами лавандового и розового
- Скругленные углы и современный дизайн
- Иконки Nerd Fonts и Font Awesome

### ⚡ **Интеграции**
- **Rofi** - запуск приложений и оконный свитчер
- **SwayNC** - центр уведомлений
- **Swaylock** - экран блокировки
- **Grim/Slurp** - создание скриншотов
- **Wlogout** - меню выхода из системы

## 🚀 Быстрая установка

### Автоматический установщик (рекомендуется)

1. **Скачайте установочный скрипт**:
```bash
curl -O https://raw.githubusercontent.com/1q2w3e4rf/config_sway/main/install.py
```

2. **Запустите установку**:
```bash
python install.py
```

3. **Следуйте инструкциям** установщика

### Что делает автоматический установщик:

- ✅ Устанавливает все необходимые зависимости через yay
- ✅ Настраивает репозитории и ключи
- ✅ Устанавливает шрифты (Nerd Fonts + Emoji)
- ✅ Копирует все конфигурационные файлы
- ✅ Настраивает системные сервисы
- ✅ Создает резервные копии существующих конфигов

## ⚙️ Ручная установка

### Предварительные требования

- Arch Linux или производные (Manjaro, EndeavourOS)
- Базовые пакеты: `base-devel`, `git`, `python`
- AUR-хелпер: `yay`

### Шаг 1: Установка зависимостей

```bash
# Основные пакеты
yay -S sway swaybg swayidle swaylock swaync \
waybar gtk-layer-shell libdbusmenu-gtk3 \
alacritty rofi wofi wlogout \
ttf-jetbrains-mono-nerd noto-fonts-emoji ttf-font-awesome \
pulseaudio pulseaudio-alsa pulseaudio-bluetooth \
pavucontrol pamixer wireplumber playerctl libpulse \
networkmanager network-manager-applet wireless_tools iwd \
blueman bluez bluez-utils brightnessctl light upower \
polkit-gnome gnome-keyring libnotify dunst grim slurp \
wf-recorder wl-clipboard clipman python python-pip \
python-dbus-next python-requests python-gobject python-i3ipc \
qt5-wayland qt6-wayland xdg-desktop-portal-wlr gtk3 \
mesa glu vulkan-radeon jq htop \
curl imv zathura zathura-pdf-mupdf nmtui \
wireguard-tools openvpn jsoncpp libmpdclient libnl \
libepoxy scdoc
```

### Шаг 2: Клонирование репозитория

```bash
git clone https://github.com/1q2w3e4rf/config_sway.git
cd config_sway
```

### Шаг 3: Копирование конфигов

```bash
# Создание директорий
mkdir -p ~/.config/{sway,waybar,rofi,alacritty,swaync}
mkdir -p ~/photo ~/.local/bin ~/.local/share/fonts

# Копирование конфигураций
cp config ~/.config/sway/
cp config.jsonc ~/.config/waybar/
cp style.css ~/.config/waybar/
cp config.rasi ~/.config/rofi/
cp swaync_config.json ~/.config/swaync/config.json
cp swaync_style.css ~/.config/swaync/style.css

# Копирование обоев
cp 1.jpg ~/photo/
```

### Шаг 4: Установка шрифтов

```bash
# Nerd Fonts
wget https://github.com/ryanoasis/nerd-fonts/releases/download/v3.0.2/JetBrainsMono.zip
unzip JetBrainsMono.zip -d ~/.local/share/fonts/

# Noto Emoji
wget https://github.com/googlefonts/noto-emoji/raw/main/fonts/NotoColorEmoji.ttf -P ~/.local/share/fonts/

# Обновление кэша шрифтов
fc-cache -fv
```

### Шаг 5: Настройка автозапуска

```bash
# Создание systemd сервиса
mkdir -p ~/.config/systemd/user
cat > ~/.config/systemd/user/sway.service << EOF
[Unit]
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
EOF

# Включение сервиса
systemctl --user enable sway.service
systemctl --user daemon-reload
sudo loginctl enable-linger $USER
```

## 🎛️ Настройка Waybar

### Модули

Конфигурация Waybar включает следующие модули:

| Модуль | Описание | Команды |
|--------|----------|---------|
| **Workspaces** | Рабочие пространства Sway | Переключение между воркспейсами |
| **Window** | Активное окно | Отображение заголовка окна |
| **Language** | Раскладка клавиатуры | `swaymsg input xkb_switch_layout` |
| **Network** | Сетевое соединение | `nmtui-connect` |
| **Weather** | Погода (wttr.in) | Открытие браузера с деталями |
| **CPU** | Загрузка процессора | Запуск `htop` |
| **Memory** | Использование памяти | Запуск `htop` |
| **PulseAudio** | Управление звуком | `pavucontrol`, `wpctl` |
| **Clock** | Время и дата | `gnome-calendar` |
| **Power** | Управление питанием | `wlogout` |

### Кастомизация модулей

#### Изменение города для погоды

Отредактируйте файл `~/.config/waybar/config.jsonc`:

```json
"custom/weather": {
    "exec": "curl -s 'wttr.in/ВашГород?format=%c+%t+%w' | sed 's/+//g'",
    "tooltip-format": "Погода в ВашемГороде:\n{}\n\nНажмите для подробностей",
    "exec-on-event": "curl -s 'wttr.in/ВашГород?format=%c+%t+%w\\n%D\\n%h\\n%p'",
    "on-click": "xdg-open 'https://wttr.in/ВашГород'"
}
```

#### Добавление новых модулей

Добавьте в соответствующий раздел `modules-left`, `modules-center` или `modules-right`:

```json
"modules-right": [
    "existing-modules",
    "custom/my-new-module"
],

"custom/my-new-module": {
    "format": "",
    "exec": "echo 'Hello World'",
    "interval": 30,
    "on-click": "some-command"
}
```

## ⌨️ Горячие клавиши

### Основные команды

| Комбинация | Действие |
|------------|----------|
| `Mod + Enter` | Запуск терминала (Alacritty) |
| `Mod + D` | Запуск приложений (Rofi) |
| `Mod + X` | Запуск браузера (Firefox) |
| `Mod + Z` | Файловый менеджер (Dolphin) |
| `Mod + V` | Запуск Steam |
| `Mod + Shift + Q` | Закрыть окно |
| `Mod + Shift + E` | Выход из Sway |

### Навигация

| Комбинация | Действие |
|------------|----------|
| `Mod + H/J/K/L` | Фокус на окно (влево/вниз/вверх/вправо) |
| `Mod + Shift + H/J/K/L` | Перемещение окна |
| `Mod + 1-0` | Переключение рабочих пространств |
| `Mod + Shift + 1-0` | Перемещение окна на workspace |

### Управление окнами

| Комбинация | Действие |
|------------|----------|
| `Mod + F` | Полноэкранный режим |
| `Mod + G` | Горизонтальное разделение |
| `Mod + T` | Вертикальное разделение |
| `Mod + S` | Режим стека |
| `Mod + W` | Режим вкладок |
| `Mod + R` | Режим изменения размеров |

### Мультимедиа

| Комбинация | Действие |
|------------|----------|
| `Print` | Скриншот экрана |
| `Mod + Print` | Скриншот области |
| `F1` | Вкл/Выкл звук |
| `F2/F3` | Громкость -/+ |
| `XF86Audio*` | Клавиши мультимедиа |

## 🎨 Кастомизация

### Изменение цветовой схемы

Отредактируйте `~/.config/waybar/style.css`:

```css
/* Основные цвета Catppuccin Macchiato */
@define-color base   #1e1e2e;
@define-color mantle #181825;
@define-color crust  #11111b;

/* Акцентные цвета */
@define-color lavender  #b4befe;
@define-color sapphire  #74c7ec;
@define-color pink      #f5c2e7;
@define-color red       #f38ba8;
```

### Изменение обоев

Замените путь к обоям в `~/.config/sway/config`:

```bash
output * bg /путь/к/вашим/обоям.jpg fill
```

### Настройка шрифтов

Измените шрифты в конфигурационных файлах:

**Waybar** (`config.jsonc`):
```json
{
    "font-family": "Your Font, Font Awesome 6 Free"
}
```

**Sway** (`config`):
```bash
font Your Font 11
```

## 🔧 Устранение неполадок

### Waybar не запускается

```bash
# Проверка ошибок
waybar -c ~/.config/waybar/config.jsonc -s ~/.config/waybar/style.css

# Просмотр логов
journalctl --user-unit=waybar -f
```

### Не работает модуль погоды

```bash
# Проверка доступности wttr.in
curl wttr.in?format=j1

# Проверка установки jq
jq --version
```

### Проблемы со звуком

```bash
# Проверка PulseAudio
pactl info

# Перезапуск звукового сервера
pulseaudio -k && pulseaudio --start
```

### Проблемы с раскладкой клавиатуры

Проверьте настройки ввода в `~/.config/sway/config`:

```bash
input * {
    xkb_layout "us,ru"
    xkb_options "grp:caps_toggle, grp:shift_caps_toggle, grp_led:caps"
}
```

## 📦 Структура проекта

```
config_sway/
├── install.py                 # Автоматический установщик
├── config                    # Основной конфиг Sway
├── config.jsonc              # Конфиг Waybar
├── style.css                 # Стили Waybar
├── config.rasi               # Конфиг Rofi
├── swaync_config.json        # Конфиг SwayNC
├── swaync_style.css          # Стили SwayNC
├── 1.jpg                     # Пример обоев
└── README.md                 # Этот файл
```

---

## 👥 Автор

**1q2w3e4rf**  
- GitHub: [https://github.com/1q2w3e4rf](https://github.com/1q2w3e4rf)  
- Конфигурация: [https://github.com/1q2w3e4rf/config_sway](https://github.com/1q2w3e4rf/config_sway)

## 🤝 Вклад

Приветствуются пул-реквесты и сообщения о проблемах! 

1. Форкните репозиторий
2. Создайте ветку для функции (`git checkout -b feature/AmazingFeature`)
3. Закоммитьте изменения (`git commit -m 'Add AmazingFeature'`)
4. Запушьте ветку (`git push origin feature/AmazingFeature`)
5. Откройте пул-реквест
---

⭐ **Если вам нравится этот проект, не забудьте поставить звезду на GitHub!**
