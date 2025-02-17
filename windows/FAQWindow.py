# Lib import
import sys
import traceback
from PyQt5.QtWidgets import QDialog
from UI.FAQ import Ui_dialog

# FAQ window class
class FAQWindow(QDialog):
    # FAQ window init
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.fui = Ui_dialog()
        self.fui.setupUi(self)
        sys.excepthook = self.handle_exception
        
    def handle_exception(self, exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            # Для прерываний типа Ctrl+C
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        error_message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        self.config.log('FAQWindow', f"Handled exception: {error_message}")
