# **Sway + Waybar Configuration: Полное руководство**

---

## **📌 Содержание**
1. [**Особенности**](#-особенности)
2. [**Установка**](#-установка)
   - [Зависимости](#-зависимости)
   - [Клонирование репозитория](#-клонирование-репозитория)
   - [Настройка окружения](#-настройка-окружения)
3. [**Настройка Waybar**](#-настройка-waybar)
   - [Модули](#модули-waybar)
   - [Кастомизация](#кастомизация-waybar)
4. [**Горячие клавиши**](#-горячие-клавиши)
5. [**Проблемы и решения**](#-проблемы-и-решения)
6. [**Дополнительные настройки**](#-дополнительные-настройки)
7. [**Скриншоты**](#-скриншоты)
8. [**Лицензия**](#-лицензия)

---

## **✨ Особенности**
✅ **Полная интеграция с Sway (Wayland)**  
✅ **Кастомный Waybar с модулями:**  
   - Рабочие пространства с иконками  
   - Медиа-контроллер (Spotify, MPV, VLC)  
   - Погода (через `wttr.in`)  
   - Системные метрики (CPU, RAM, температура)  
   - Управление звуком (`pamixer`)  
   - Индикатор раскладки клавиатуры  
   - Уведомления (`swaync`)  
✅ **Горячие клавиши в стиле Vim**  
✅ **Поддержка тачпада (жесты, тапы)**  
✅ **Интеграция с Rofi (запуск приложений)**  
✅ **Автоматические скриншоты (`grim + slurp`)**  
✅ **Темная тема Catppuccin Mocha**  

---

## **🛠 Установка**

### **📦 Зависимости**
Перед установкой убедитесь, что у вас есть:
- **Sway** (Wayland-композитор)  
- **Waybar** (кастомная панель)  
- **Дополнительные утилиты**  

#### **1. Установка основных пакетов (для Arch Linux)**
```bash
sudo pacman -S sway waybar rofi alacritty grim slurp wlogout playerctl pamixer pulseaudio-alsa networkmanager nm-connection-editor nmtui jq ttf-jetbrains-mono-nerd noto-fonts-emoji python-pywal wget curl
```

#### **2. Установка дополнительных скриптов**
- **Для управления подсветкой экрана**:
  ```bash
  sudo pacman -S brightnessctl
  ```
- **Для уведомлений** (опционально):
  ```bash
  sudo pacman -S swaync
  ```

#### **3. Установка шрифтов (Nerd Fonts)**
```bash
yay -S ttf-nerd-fonts-symbols
```

---

### **📥 Клонирование репозитория**
```bash
git clone https://github.com/yourusername/config_sway.git ~/.config/sway
git clone https://github.com/yourusername/waybar-config.git ~/.config/waybar
```

---

### **⚙️ Настройка окружения**
1. **Проверьте, что Sway запускается**:
   ```bash
   sway
   ```
2. **Добавьте автозагрузку Waybar**:
   В файле `~/.config/sway/config` убедитесь, что есть строка:
   ```bash
   exec waybar
   ```
3. **Дайте права на скрипты**:
   ```bash
   chmod +x ~/.config/sway/scripts/*
   chmod +x ~/.config/waybar/modules/*
   ```

---

## **🎛 Настройка Waybar**

### **🔧 Модули Waybar**
| Модуль | Описание | Зависимости |
|--------|----------|-------------|
| **Рабочие пространства** | Иконки + подсветка активного | `sway` |
| **Окно** | Название текущего окна | `sway` |
| **Медиа** | Управление плеерами (`playerctl`) | `playerctl` |
| **Погода** | Данные с `wttr.in` | `curl`, `jq` |
| **Сеть** | Статус Wi-Fi/Ethernet | `networkmanager` |
| **Звук** | Громкость (`pamixer`) | `pamixer`, `pulseaudio` |
| **Язык** | Раскладка клавиатуры | `swaymsg` |
| **Уведомления** | Индикатор (`swaync`) | `swaync` |

---

### **🎨 Кастомизация Waybar**
1. **Изменить город для погоды**:
   В `~/.config/waybar/config` замените:
   ```json
   "exec": "curl -s 'wttr.in/Vyazniki?format=%c+%t+%w'"
   ```
   на свой город (например, `Moscow`).

2. **Поменять цветовую схему**:
   Редактируйте `~/.config/waybar/style.css`.  
   Доступные цвета (Catppuccin Mocha):
   ```css
   @define-color base #1e1e2e;
   @define-color text #cdd6f4;
   @define-color lavender #b4befe;
   ```

3. **Добавить/удалить модули**:
   В `~/.config/waybar/config` измените `modules-left`, `modules-center`, `modules-right`.

---

## **⌨️ Горячие клавиши**
| Комбинация | Действие |
|------------|----------|
| `Mod + Enter` | Терминал (`alacritty`) |
| `Mod + D` | Запуск приложений (`rofi`) |
| `Mod + X` | Браузер (`firefox`) |
| `Mod + Z` | Файловый менеджер (`dolphin`) |
| `Mod + C` | Bitwarden |
| `Mod + 1-0` | Переключение рабочих пространств |
| `Print` | Скриншот (`grim`) |
| `Mod + Print` | Скриншот области (`slurp`) |
| `Mod + R` | Режим изменения размеров окна |

---

## **⚠️ Проблемы и решения**
### **1. Waybar не запускается**
- **Проверьте зависимости**:
  ```bash
  waybar --version
  ```
- **Логи**:
  ```bash
  journalctl -u waybar -f
  ```
- **Запуск вручную**:
  ```bash
  waybar -c ~/.config/waybar/config -s ~/.config/waybar/style.css
  ```

### **2. Не работает модуль погоды**
- Убедитесь, что есть интернет:
  ```bash
  curl wttr.in
  ```
- Проверьте, что `jq` установлен:
  ```bash
  jq --version
  ```

### **3. Не меняется раскладка клавиатуры**
Проверьте настройки ввода в `~/.config/sway/config`:
```bash
input * {
    xkb_layout "us,ru"
    xkb_options "grp:caps_toggle"
}
```

---

## **🔧 Дополнительные настройки**
### **1. Автозапуск приложений**
Добавьте в `~/.config/sway/config`:
```bash
exec telegram-desktop
exec firefox
```

### **2. Изменить обои**
Замените путь в `~/.config/sway/config`:
```bash
output * bg /path/to/wallpaper.jpg fill
```

---

## **🖼 Скриншоты**
(Добавьте свои скриншоты интерфейса)

---

## **📜 Лицензия**
MIT License.  
Автор: [Ваш ник] | GitHub: [ссылка]  

---

Этот `README.md` полностью готов к публикации на GitHub.  
Можно добавить скриншоты, GIF-демонстрации и ссылки на дополнительные ресурсы. 🚀
