# Lib import
from PyQt5.QtWidgets import QDialog
from UI.FAQ import Ui_dialog

# FAQ window class
class FAQWindow(QDialog):
    # FAQ window init
    def __init__(self):
        super().__init__()
        self.fui = Ui_dialog()
        self.fui.setupUi(self)
