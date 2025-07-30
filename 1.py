import os
import shutil
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Пути (замени 'rek' на своё имя пользователя)
DOWNLOADS_PATH = os.path.expanduser("~/Downloads")  # Откуда берём файлы
TARGET_BASE_PATH = "/home/rek"                     # Куда сортируем (папки должны существовать!)

# Категории и их папки (папки должны быть в /home/rek/)
CATEGORIES = {
    "Documents": ["Documents", "Документы"],
    "Images": ["Pictures", "Images", "Фото"],
    "Music": ["Music", "Музыка"],
    "Videos": ["Videos", "Видео"],
    "Archives": ["Archives", "Архивы"],
    "Torrents": ["Torrents"],
    "Programs": ["Programs", "Программы"],
    "Books": ["Books", "Книги"],
    "Scripts": ["Scripts", "Скрипты"],
}

# Расширения файлов (добавлены новые категории)
EXTENSIONS = {
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".ppt", ".pptx", ".csv"],
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".svg", ".heic"],
    "Music": [".mp3", ".flac", ".wav", ".aac", ".ogg", ".m4a", ".wma"],
    "Videos": [".mp4", ".mkv", ".mov", ".avi", ".wmv", ".flv", ".webm", ".m4v", ".3gp"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"],
    "Torrents": [".torrent"],
    "Programs": [".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm", ".apk"],
    "Books": [".epub", ".mobi", ".fb2", ".djvu"],
    "Scripts": [".py", ".sh", ".bat", ".ps1", ".js", ".php", ".html", ".css"],
}

class DownloadHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            time.sleep(1)  # Даём время на завершение загрузки
            process_file(event.src_path)

def find_target_folder(category):
    """Ищет существующую папку для категории в /home/rek/"""
    for folder in CATEGORIES.get(category, []):
        full_path = os.path.join(TARGET_BASE_PATH, folder)
        if os.path.exists(full_path):
            return full_path
    return None

def get_file_category(file_extension):
    """Определяет категорию файла по расширению"""
    file_extension = file_extension.lower()
    for category, extensions in EXTENSIONS.items():
        if file_extension in extensions:
            return category
    return "Other"

def process_file(file_path):
    """Обрабатывает один файл"""
    filename = os.path.basename(file_path)
    
    # Пропускаем скрытые файлы
    if filename.startswith('.'):
        return
    
    # Определяем категорию
    _, extension = os.path.splitext(filename)
    category = get_file_category(extension)
    
    # Ищем целевую папку
    target_folder = find_target_folder(category)
    if not target_folder:
        print(f"⚠ Папка для категории '{category}' не найдена в {TARGET_BASE_PATH}")
        return
    
    # Перемещаем файл
    try:
        shutil.move(file_path, target_folder)
        print(f"✅ Перемещён: {filename} → {target_folder}")
    except Exception as e:
        print(f"❌ Ошибка при перемещении {filename}: {e}")

def initial_sort():
    """Первоначальная сортировка всех файлов в Downloads"""
    print("🔄 Начальная сортировка файлов в Downloads...")
    for filename in os.listdir(DOWNLOADS_PATH):
        file_path = os.path.join(DOWNLOADS_PATH, filename)
        if os.path.isfile(file_path):
            process_file(file_path)
    print("✅ Первоначальная сортировка завершена!")

def start_monitoring():
    """Запускает мониторинг папки Downloads"""
    event_handler = DownloadHandler()
    observer = Observer()
    observer.schedule(event_handler, DOWNLOADS_PATH, recursive=False)
    observer.start()
    print("👀 Начат мониторинг папки Downloads...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    # Создаём папку Other если её нет
    other_folder = os.path.join(TARGET_BASE_PATH, "Other")
    if not os.path.exists(other_folder):
        os.makedirs(other_folder)
    
    initial_sort()
    start_monitoring()
