# Lib import
import math
import os
import shutil
import pathlib
import re
import subprocess
import sys
import webbrowser
from pathlib import Path
from elevate import elevate

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QMessageBox, QApplication, QDialog, QMainWindow

from FAQ import Ui_dialog
from normUI2 import Ui_MainWindow


class FAQWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.fui = Ui_dialog()
        self.fui.setupUi(self)


def ffmpeg_install():
    if not "c:\\ffmpeg\\bin" in os.environ["PATH"].lower():
        os.environ["PATH"] += os.pathsep + os.pathsep.join(["c:\\ffmpeg\\bin"])
        if not os.path.exists("c:\\ffmpeg\\bin"):
            shutil.copytree(Path(pathlib.Path.cwd(), 'ffmpeg'), Path("c:\\ffmpeg\\"))


# GUI Class
class MainWindow(QMainWindow):  # Program window
    def __init__(self):
        super().__init__()
        elevate()
        ffmpeg_install()
        self.hardsub_dir = Path(pathlib.Path.cwd(), 'HARDSUB')
        self.main_dir = Path(pathlib.Path.cwd())
        self.hard_only = False
        self.soft_hard = True
        self.compile_var = False
        self.hardsubber = False
        self.finish_message = False
        self.sub = None
        self.Nvenc = None
        self.noSound = None
        self.threadMain = None
        self.faqWindow = None
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.set_buttons()
        self.base = [
            self.ui.startButton,
            self.ui.bitrateBox,
            self.ui.modeBox,
            self.ui.hardCheck,
            self.ui.nvencCheck,
            self.ui.rawButton,
            self.ui.softButton,
            self.ui.soundButton,
            self.ui.subButton,
            self.ui.episodeLine,
            self.ui.rawPath,
            self.ui.soundPath,
            self.ui.subPath,
            self.ui.softPath
        ]
        self.ui.stopButton.hide()

    def open_faq(self):
        if self.faqWindow is None:
            self.faqWindow = FAQWindow()
        self.faqWindow.show()

    # Buttons definition
    def set_buttons(self):
        self.ui.hardfolderButton.clicked.connect(self.open_hardsub)
        self.ui.stopButton.clicked.connect(self.proc_kill)
        self.ui.startButton.clicked.connect(self.ffmpeg_thread)
        self.ui.softButton.clicked.connect(self.soft_folder_path)
        self.ui.soundButton.clicked.connect(self.sound_folder_path)
        self.ui.rawButton.clicked.connect(self.raw_folder_path)
        self.ui.subButton.clicked.connect(self.sub_folder_path)
        self.ui.siteButton.clicked.connect(lambda: webbrowser.open
        ('https://www.youtube.com/watch?v=jQ6gPyYNgPo&ab_channel=Antihero'))
        self.ui.pushButton_rick.clicked.connect(lambda: webbrowser.open
        ('https://www.youtube.com/watch?v=o-YBDTqX_ZU&t=1s'))
        self.ui.faqButton.clicked.connect(self.open_faq)

    # Open hardsub directory
    def open_hardsub(self):
        if os.path.exists(self.hardsub_dir):
            os.startfile(self.hardsub_dir)
        else:
            self.coding_error('hardsub_folder')

    # Softsub saving path
    def soft_folder_path(self):
        soft_path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Куда пихать софт?')
        self.ui.softPath.setText(soft_path)

    # Sound file choose
    def sound_folder_path(self):
        sound_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Где брать звук?", "",
                                                              "All(*.wav *.flac *.aac *.m4a *.mka)")
        self.ui.soundPath.setText(sound_path)

    # Raw video choose
    def raw_folder_path(self):
        raw_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Где брать равку?", "",
                                                            "ALL (*.mkv *.mp4 *.avi)")
        self.ui.rawPath.setText(raw_path)

    # Subtitle choose
    def sub_folder_path(self):
        sub_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Где брать надписи?", "",
                                                            "Хуй (*.ass *.srt)")
        self.ui.subPath.setText(sub_path)

    def coding_error(self, error_type):
        self.ui.stateLabel.setText("МЕГАПЛОХ!")
        msg = QMessageBox()
        msg.setWindowTitle("Чел ты...")
        msg.setIcon(QMessageBox.Warning)
        match error_type:
            case 'softsub':
                msg.setText("Выбери куда сохранять софтсаб!")
                msg.setStandardButtons(QMessageBox.Open)
                msg.buttonClicked.connect(self.soft_folder_path)
            case 'subtitle':
                msg.setText("Выбери путь к файлу субтитров!")
                msg.setStandardButtons(QMessageBox.Open)
                msg.buttonClicked.connect(self.sub_folder_path)
            case 'raw':
                msg.setText("Выбери путь к равке!")
                msg.setStandardButtons(QMessageBox.Open)
                msg.buttonClicked.connect(self.raw_folder_path)
            case 'sound':
                msg.setText("Выбери путь к дорожке звука!")
                msg.setStandardButtons(QMessageBox.Open)
                msg.buttonClicked.connect(self.sound_folder_path)
            case 'name':
                msg.setText("Напиши имя релиза!")
                msg.setStandardButtons(QMessageBox.Ok)
            case 'hardsub_folder':
                msg.setText("НАХУЯ ТЫ ПАПКИ УДАЛЯЕШЬ?!")
                msg.setStandardButtons(QMessageBox.Ok)
                os.mkdir('HARDSUB')
            case 'stop':
                msg.setText("Зачем остановил?!")
                msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    # Thread start with ffmpeg
    def ffmpeg_thread(self):
        if os.path.exists(self.hardsub_dir):
            self.ui.stateLabel.setText("Работаю....(наверное)")
            self.ui.progressBar.setValue(0)
        else:
            self.coding_error('hardsub_folder')

        self.Nvenc = 'h264_nvenc' if self.ui.nvencCheck.isChecked() else 'libx264'
        self.sub = self.ui.hardCheck.isChecked()

        match self.ui.modeBox.currentText():
            case 'Софт и хард':
                self.soft_hard = True
                self.hard_only = False
                self.compile_var = False
            case 'Только хард':
                self.soft_hard = False
                self.hard_only = True
                self.compile_var = False
            case 'Только софт':
                self.soft_hard = False
                self.hard_only = False
                self.compile_var = True
            case 'Для хардсабберов':
                self.hardsubber = True

        if self.ui.episodeLine.text():
            if self.ui.soundPath.text() or self.hardsubber:
                if self.ui.rawPath.text():
                    if self.ui.subPath.text() and self.sub:
                        if self.ui.softPath.text() or self.hard_only or self.hardsubber:
                            self.threadMain = ThreadClassSoft(self.ui.episodeLine.text(), self.ui.rawPath.text(),
                                                              self.ui.soundPath.text(), self.ui.subPath.text(),
                                                              self.ui.softPath.text(), self.ui.bitrateBox.currentText(),
                                                              self.Nvenc, self.sub, self.compile_var,
                                                              self.soft_hard, self.hard_only, self.hardsubber)
                            self.threadMain.finished.connect(self.finished)
                            self.threadMain.frame_upd.connect(self.frame_update)
                            self.threadMain.time_upd.connect(self.time_update)
                            self.locker(True)
                            self.ui.startButton.hide()
                            self.ui.stopButton.show()
                            self.threadMain.start()
                        else:
                            self.coding_error('softsub')
                    else:
                        self.coding_error('subtitle')
                else:
                    self.coding_error('raw')
            else:
                self.coding_error('sound')
        else:
            self.coding_error('name')

    # Progress update
    def frame_update(self, frame):
        self.ui.progressBar.setValue(0)
        f1 = str(frame).replace('frame=', '').replace(' ', '')
        value = math.ceil(float(f1))
        self.ui.progressBar.setValue(value)

    # Set progressbar maximum
    def time_update(self, time):
        self.ui.progressBar.setMaximum(math.ceil(time))

    def proc_kill(self):
        os.chdir(self.main_dir)
        self.finish_message = True
        ffmpeg_kill = 'taskkill /f /im ffmpeg.exe'
        subprocess.run(ffmpeg_kill, shell=True)

    # After coding
    def finished(self):
        os.chdir(self.main_dir)
        self.ui.startButton.show()
        self.ui.stopButton.hide()

        if self.finish_message:
            self.coding_error('stop')
            self.finish_message = False
        else:
            self.ui.stateLabel.setText("Все готово!")
            QApplication.beep()

        self.ui.progressBar.setValue(0)
        self.locker(False)

    # Blocking strings and buttons while coding
    def locker(self, lock_value):
        for item in self.base:
            item.setDisabled(lock_value)
        self.ui.stopButton.setDisabled(not lock_value)


# Coding class with thread
class ThreadClassSoft(QThread):
    # Signals
    frame_upd = QtCore.pyqtSignal(object)
    time_upd = QtCore.pyqtSignal(object)

    def __init__(self, name, raw, sound, sub, soft, rate, nvenc, hard, compile_var, soft_hard, hard_only, hardsubber):
        super(ThreadClassSoft, self).__init__()
        self.path_hard = Path(pathlib.Path.cwd(), 'HARDSUB')
        self.sub_name = None
        self.soft_path = soft
        self.name = name
        self.raw_path = raw
        self.sound_path = sound
        self.sub_path = sub
        self.rate = rate
        self.nvenc = nvenc
        self.hard = hard
        self.compile_var = compile_var
        self.soft_hard = soft_hard
        self.hard_only = hard_only
        self.hardsubber = hardsubber

    def softsub(self):
        if self.compile_var or self.soft_hard:
            if self.hard:
                cmd = f'ffmpeg -y -i "{self.raw_path}" -i "{self.sound_path}" -i "{self.sub_path}" -map 0:v -map 1:a ' \
                      f'-metadata:s:v:0 title="Original" ' \
                      f'-map 2:s -metadata:s:s:0 language=rus  -metadata:s:s:0 title="Caption" -c:s ' \
                      f'copy -metadata:s:v:0 language=jap -metadata:s:a:0 title="AniBaza" -metadata:s:a:0 language=rus ' \
                      f'-metadata title="{self.name}" -c:a aac -b:a 320K -ar 48000 -c:v copy ' \
                      f'-pix_fmt ' \
                      f'yuv420p "{self.soft_path}/{self.name}.mkv"'
            else:
                cmd = f'ffmpeg -y -i "{self.raw_path}" -i "{self.sound_path}" -map 0:v -map 1:a ' \
                      f'-metadata:s:v:0 title="Original" ' \
                      f'-metadata:s:v:0 language=jap -metadata:s:a:0 title="AniBaza" -metadata:s:a:0 language=rus ' \
                      f'-metadata title="{self.name}" -c:a aac -b:a 320K -ar 48000 -c:v copy ' \
                      f'-pix_fmt ' \
                      f'yuv420p "{self.soft_path}/{self.name}.mkv"'
            p1 = subprocess.Popen(cmd,
                                  shell=True,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT,
                                  universal_newlines=True,
                                  encoding='utf-8',
                                  )
            for line in p1.stdout:
                f1 = re.search(r'frame=\s?\s?\s?\s?\d+', line)
                l1 = re.search(r'Duration:\s\d{2}.\d{2}.\d{2}.\d{2}\b', line)
                if l1 is not None:
                    l2 = str(l1.group())
                    l3 = l2.replace('Duration: ', '').split(':')
                    hrs = float(l3[0]) * 3600
                    minutes = float(l3[1]) * 60
                    sec = float(l3[2])
                    dur = hrs + minutes + sec
                    frame = dur * 23.98
                    self.time_upd.emit(frame)
                if f1 is not None:
                    self.frame_upd.emit(f1.group())

    def hardsubbering(self):
        if self.hardsubber:
            command_list_hardsub = \
                'ffmpeg', '-y', \
                    '-i', f'{self.raw_path}', \
                    '-vf', f'subtitles={self.sub_name}', \
                    f'{self.path_hard}/{self.name}.mp4'
            p3 = subprocess.Popen(command_list_hardsub,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT,
                                  universal_newlines=True,
                                  shell=True,
                                  encoding='utf-8'
                                  )
            for line in p3.stdout:
                print(line)
                f1 = re.search(r'frame=\s?\s?\s?\s?\d+', line)
                l1 = re.search(r'Duration:\s\d{2}.\d{2}.\d{2}.\d{2}\b', line)
                if l1 is not None:
                    l2 = str(l1.group())
                    l3 = l2.replace('Duration: ', '').split(':')
                    hrs = float(l3[0]) * 3600
                    minutes = float(l3[1]) * 60
                    sec = float(l3[2])
                    dur = hrs + minutes + sec
                    frame = dur * 23.98
                    self.time_upd.emit(frame)
                if f1 is not None:
                    self.frame_upd.emit(f1.group())




    def hardsub(self):
        if self.hard_only or self.soft_hard:
            if self.hard:
                command_list_hardsub = \
                    'ffmpeg', '-y', \
                    '-i', f'{self.raw_path}', \
                    '-i', f'{self.sound_path}', \
                    '-map', '0:v', \
                    '-map', '1:a', \
                    '-vf', f'subtitles={self.sub_name}', \
                    '-c:a', 'aac', \
                    '-b:a', '320K', \
                    '-ar', '48000', \
                    '-c:v', f'{self.nvenc}', \
                    '-b:v', f'{self.rate}K', \
                    '-pix_fmt', 'yuv420p', \
                    f'{self.path_hard}/{self.name}.mp4'
            else:
                command_list_hardsub = \
                    'ffmpeg', '-y', \
                    '-i', f'{self.raw_path}', \
                    '-i', f'{self.sound_path}', \
                    '-map', '0:v', \
                    '-map', '1:a', \
                    '-c:a', 'aac', \
                    '-b:a', '320K', \
                    '-ar', '48000', \
                    '-c:v', f'{self.nvenc}', \
                    '-b:v', f'{self.rate}K', \
                    '-pix_fmt', 'yuv420p', \
                    f'{self.path_hard}/{self.name}.mp4'
            p2 = subprocess.Popen(command_list_hardsub,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT,
                                  universal_newlines=True,
                                  shell=True,
                                  encoding='utf-8'
                                  )
            for line in p2.stdout:
                f1 = re.search(r'frame=\s?\s?\s?\s?\d+', line)
                l1 = re.search(r'Duration:\s\d{2}.\d{2}.\d{2}.\d{2}\b', line)
                if l1 is not None:
                    l2 = str(l1.group())
                    l3 = l2.replace('Duration: ', '').split(':')
                    hrs = float(l3[0]) * 3600
                    minutes = float(l3[1]) * 60
                    sec = float(l3[2])
                    dur = hrs + minutes + sec
                    frame = dur * 23.98
                    self.time_upd.emit(frame)
                if f1 is not None:
                    self.frame_upd.emit(f1.group())

    # Coding commands
    def run(self):
        os.chdir(os.path.dirname(self.sub_path))
        self.sub_name = os.path.basename(self.sub_path)
        a = (str(self.sub_name).replace('[', '').replace(']', ''))
        b = str(Path(pathlib.Path.cwd(), 'tmp'))

        os.popen(f'copy {self.sub_name} {b}/{a}')

        self.softsub()
        self.hardsub()
        self.hardsubbering()


# Standard code
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
