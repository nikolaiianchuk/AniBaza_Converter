import os

from datetime import datetime

class LoggingModule:
    def __init__(self):
        self.log_file = None
        self.log_filename = None
        self.logs_dir = None
        self.log_flag = False
        self.max_logs = None
    
    def start_logging(self, input_flag, logs_dir, max_logs):
        self.logs_dir = logs_dir
        self.max_logs = max_logs
        self.log_flag = input_flag
        if self.log_flag:
            # Создание папки logs, если её нет
            if not os.path.exists(self.logs_dir):
                os.makedirs(self.logs_dir)

            log_files = sorted(os.listdir(self.logs_dir))

            # Убираем старые файлы, если их больше чем max_logs
            if len(log_files) >= self.max_logs:
                # Получаем файлы, которые нужно удалить
                files_to_delete = log_files[:-self.max_logs]
                for file in files_to_delete:
                    file_path = os.path.join(self.logs_dir, file)
                    os.remove(file_path)
                    print(f"Удален старый лог файл: {file_path}")
            
            # Генерация имени файла по дате и времени
            self.log_filename = datetime.now().strftime(f"logs/mainlog_%Y-%m-%d_%H-%M-%S.txt")
            
            # Открываем файл для записи логов
            self.log_file = open(self.log_filename, 'a', encoding="utf-8")
            
            self.write_to_log("LoggingModule", f"Logging started in {self.log_filename}")
        
    def write_to_log(self, topic="", message=""):
        if self.log_flag and self.log_file:
            print(f"[{topic}]: {message}")
            self.log_file.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}][{topic}]: {message}\n".encode("utf-8", "replace").decode("utf-8"))
        
    def stop_logging(self):
        if self.log_flag and self.log_file:
            self.write_to_log("LoggingModule", "Logging stopped.")
            self.log_file.close()
            self.remove_empty_lines_from_log(self.log_filename)

    def remove_empty_lines_from_log(self, file_path):
        # Удаляет пустые строки из файла.
        try:
            # Чтение содержимого файла
            with open(file_path, 'r') as file:
                lines = file.readlines()
            
            # Фильтрация пустых строк
            non_empty_lines = [line for line in lines if line.strip()]
            
            # Запись обратно в файл без пустых строк
            with open(file_path, 'w') as file:
                file.writelines(non_empty_lines)
            
            print(f"Удалены пустые строки из файла: {file_path}")
        except Exception as e:
            print(f"Ошибка при обработке файла: {e}")
            