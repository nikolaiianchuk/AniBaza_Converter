# Lib import
import pathlib
import sys
import ctypes

from pathlib import Path
from PyQt5 import QtWidgets
from mainWindow import MainWindow

# Admin check
def is_admin():
    # Проверяет, запущен ли скрипт с правами администратора
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception as e:
        print(f"Ошибка проверки прав администратора: {e}")
        return False

# Main function
def main():
    try:
        app = QtWidgets.QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(True)
        mainWindow = MainWindow()
        mainWindow.show()
        sys.exit(app.exec_())
    except Exception as e:
        input()
        print(e)

# Standard code
if __name__ == "__main__":
    if not is_admin():
        # Перезапускаем скрипт с правами администратора
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    else:
        main()
