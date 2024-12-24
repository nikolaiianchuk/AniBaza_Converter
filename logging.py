import config
import os
import sys

from datetime import datetime

def start_logging():
    max_logs = 49
    
    # Создание папки logs, если её нет
    if not os.path.exists(config.logs_dir):
        os.makedirs(config.logs_dir)

    log_files = sorted(os.listdir(config.logs_dir))

    # Убираем старые файлы, если их больше чем max_logs
    if len(log_files) > max_logs:
        # Получаем файлы, которые нужно удалить
        files_to_delete = log_files[:-max_logs]
        for file in files_to_delete:
            file_path = os.path.join(config.logs_dir, file)
            os.remove(file_path)
            print(f"Удален старый лог файл: {file_path}")
    
    # Генерация имени файла по дате и времени
    log_filename = datetime.now().strftime(f"logs/mainlog_%Y-%m-%d_%H-%M-%S.txt")

    # Открываем файл для записи логов
    log_file = open(log_filename, 'a')

    # Перенаправляем stdout и stderr в файл
    sys.stdout = log_file
    sys.stderr = log_file

    print(f"Logging started in {log_filename}")