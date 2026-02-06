import math
import os
import re
import subprocess
import sys
import traceback
import webbrowser

import modules.ConfigModule as ConfigModule

from modules.GlobalExceptionHandler import get_global_handler
from typing import Optional
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox, QApplication, QMainWindow
from UI.normUI2 import Ui_MainWindow
from windows.FAQWindow import FAQWindow
from threads.RenderThread import ThreadClassRender
from modules.AppUpdater import UpdaterUI
from models.protocols import ProcessRunner
from models.render_paths import RenderPaths
from models.job_queue import JobQueue
from threads.QueueProcessor import QueueProcessor
from widgets.job_queue_widget import JobQueueWidget

# Main window class
class MainWindow(QMainWindow):
    # Main window init
    def __init__(self, config, runner: Optional[ProcessRunner] = None):
        super().__init__()
        get_global_handler().register_callback(self.handle_exception)
        self.config = config
        self.runner = runner
        self.finish_message = False
        self.threadMain = None
        self.faqWindow = None
        self.first_show = True

        # UI path state (not stored on config)
        self._ui_paths = {
            'raw': '',
            'audio': '',
            'sub': '',
        }
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Initialize queue components
        self.job_queue = JobQueue()
        self.queue_processor = QueueProcessor(self.job_queue)
        self.queue_widget = JobQueueWidget()

        # Connect queue processor signals
        self.queue_processor.job_started.connect(self.on_job_started)
        self.queue_processor.job_completed.connect(self.on_job_completed)
        self.queue_processor.job_failed.connect(self.on_job_failed)
        self.queue_processor.job_cancelled.connect(self.on_job_cancelled)
        self.queue_processor.queue_finished.connect(self.on_queue_finished)

        # Connect queue widget signals
        self.queue_widget.move_up_requested.connect(self.on_move_up_requested)
        self.queue_widget.move_down_requested.connect(self.on_move_down_requested)
        self.queue_widget.remove_requested.connect(self.on_remove_requested)
        self.queue_widget.stop_requested.connect(self.on_stop_requested)
        self.queue_widget.clear_completed_requested.connect(self.on_clear_completed_requested)

        self.set_buttons()
        self.set_checkboxes()
        self.set_textboxes()
        self.set_comboboxes()
        self.base = [
            self.ui.render_start_button,
            self.ui.render_mode_box,
            self.ui.nvenc_box,
            self.ui.logo_box,
            self.ui.app_ffmpeg_update_check,
            self.ui.raw_path_open_button,
            self.ui.softsub_path_open_button,
            self.ui.audio_path_open_button,
            self.ui.subtitle_path_open_button,
            self.ui.episode_line,
            self.ui.raw_path_editline,
            self.ui.audio_path_editline,
            self.ui.subtitle_path_editline,
            self.ui.softsub_path_editline,
            self.ui.config_save_button
        ]
        self.ui.render_stop_button.hide()
        self.ui.app_version_label.setText("Version {NUM} ({NAME}) by {AUTHOR}".format(
            NUM    = self.config.app_info.version_number,
            NAME   = self.config.app_info.version_name,
            AUTHOR = self.config.app_info.author
        ))
        self.setWindowTitle(self.config.app_info.title)

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            # Для прерываний типа Ctrl+C
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        error_message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        self.config.log('mainWindow', 'handle_exception', f"Handled exception: {error_message}")
        self.ui.app_state_label.setText("ОШИБКА! См. лог файлы.")

    def showEvent(self, event):
        super().showEvent(event)
        if self.first_show:  # Проверяем, был ли уже вызван showEvent
            self.first_show = False  # Сбрасываем флаг, чтобы не выполнять повторно
            self.updater_ui = UpdaterUI(self, self.config)
            if self.config.update_search:
                self.updater_ui.start_updater()
            else:
                self.config.log('mainWindow', 'showEvent', "Updater disabled.")

    def universal_update(self, setting_path, value, log_message, type, post_operation=None):
        # Handle UI paths specially - store locally, not on config
        if setting_path.startswith('rendering_paths.'):
            path_key = setting_path.split('.')[1]
            self._ui_paths[path_key] = value
        else:
            keys = setting_path.split('.')
            setting = self.config
            for key in keys[:-1]:
                if isinstance(setting, dict):
                    setting = setting.setdefault(key, {})
                else:
                    setting = getattr(setting, key, None)
            last_key = keys[-1]
            if isinstance(setting, dict):
                setting[last_key] = value
            else:
                setattr(setting, last_key, value)

        if log_message:
            if type == "checkbox":
                self.config.log('mainWindow', 'universal_update', log_message.format(VALUE="enabled" if value else "disabled"))
            elif type == "textbox":
                self.config.log('mainWindow', 'universal_update', log_message.format(VALUE=value))
            elif type == "combobox":
                self.config.log('mainWindow', 'universal_update', log_message)

        post_operation() if post_operation else None

    def universal_setter(self, ui, value, log_message, type, post_operation=None):
        match type:
            case "checkbox":
                ui.setChecked(value)
                self.config.log('mainWindow', 'universal_setter', log_message.format(VALUE="enabled" if value else "disabled"))

        post_operation() if post_operation else None

    # Softsub path updater
    def soft_path_constructor(self):
        if '[AniBaza]' in self.config.main_paths.softsub:
            self.config.build_settings.episode_name = self.config.main_paths.softsub.split('/')[-1]
            self.config.build_settings.episode_name = self.config.build_settings.episode_name.replace(
                self.config.build_settings.episode_name[self.config.build_settings.episode_name.rfind('[')+1 :
                self.config.build_settings.episode_name.rfind(']')],''
            ) if '[' in self.config.build_settings.episode_name else self.config.build_settings.episode_name
            self.ui.episode_line.setText(self.config.build_settings.episode_name)
        else:
            self.config.log('mainWindow', 'soft_path_constructor', f"Softsub base path updated to: {self.config.main_paths.softsub}")
        self.update_render_paths()

    def update_render_paths(self):
        self.config.rendering_paths['softsub'] = f"{self.config.main_paths.softsub}/{self.config.build_settings.episode_name}.mkv"
        self.config.log('mainWindow', 'update_render_paths', f"Softsub render path updated to: {self.config.rendering_paths['softsub']}")
        self.config.rendering_paths['hardsub'] = f"{self.config.main_paths.hardsub}/{self.config.build_settings.episode_name}.mp4"
        self.config.log('mainWindow', 'update_render_paths', f"Hardsub render path updated to: {self.config.rendering_paths['hardsub']}")
        self.config.log('mainWindow', 'update_render_paths', 'Render paths updated!')

    def lock_mode(self):
        ui_for_disable = (
            self.ui.audio_path_editline,
            self.ui.audio_path_open_button,
            self.ui.softsub_path_editline,
            self.ui.softsub_path_open_button
        )
        for ui in ui_for_disable:
            ui.setDisabled(self.config.build_settings.build_state == 3)

    # FAQ window opener
    def open_faq(self):
        if self.faqWindow is None:
            self.faqWindow = FAQWindow(self.config)
        self.faqWindow.show()
        self.config.log('mainWindow', 'open_faq', "FAQ window opened.")

    # Buttons definition
    def set_buttons(self):
        buttons = {
            self.ui.hardsub_folder_open_button: self.open_hardsub,
            self.ui.logs_folder_open_button: self.open_logsdir,
            self.ui.render_stop_button: self.proc_kill,
            self.ui.render_start_button: self.ffmpeg_thread,
            self.ui.softsub_path_open_button: self.soft_folder_path,
            self.ui.audio_path_open_button: self.sound_folder_path,
            self.ui.raw_path_open_button: self.raw_folder_path,
            self.ui.subtitle_path_open_button: self.sub_folder_path,
            self.ui.anibaza_site_open_button: lambda: webbrowser.open('https://www.youtube.com/watch?v=jQ6gPyYNgPo'),
            self.ui.rickroll_button: lambda: webbrowser.open('https://www.youtube.com/watch?v=o-YBDTqX_ZU'),
            self.ui.FAQ_open_button: self.open_faq,
            self.ui.config_save_button: lambda: ConfigModule.save_config(self.config)
        }

        for button, handler in buttons.items():
            button.clicked.connect(handler)

        self.config.log('mainWindow', 'set_buttons', "Buttons set.")

    # Checkboxes definition
    def set_checkboxes(self):
        checkboxes = {
            self.ui.dev_mode_enable: (
                lambda: self.universal_update(
                    'dev_settings.dev_mode',
                    self.ui.dev_mode_enable.isChecked(),
                    "Dev mode {VALUE}.",
                    "checkbox",
                    lambda: self.ui.log_mode_enable.setEnabled(self.config.dev_settings.dev_mode)
                ),
                lambda: self.universal_setter(
                    self.ui.dev_mode_enable,
                    self.config.dev_settings.dev_mode,
                    "Dev mode {VALUE}.",
                    "checkbox"
                )
            ),
            self.ui.log_mode_enable: (
                lambda: self.universal_update(
                    'dev_settings.logging.state',
                    self.ui.log_mode_enable.isChecked(),
                    "Logging mode {VALUE}.",
                    "checkbox"
                ),
                lambda: self.universal_setter(
                    self.ui.log_mode_enable,
                    self.config.dev_settings.logging_enabled,
                    "Logging mode {VALUE}.",
                    "checkbox"
                )
            ),
            self.ui.app_ffmpeg_update_check: (
                lambda: self.universal_update(
                    'update_search',
                    self.ui.app_ffmpeg_update_check.isChecked(),
                    "Update search {VALUE}.",
                    "checkbox"
                ),
                lambda: self.universal_setter(
                    self.ui.app_ffmpeg_update_check,
                    self.config.update_search,
                    "Updater {VALUE}.",
                    "checkbox"
                )
            ),
            self.ui.potatoPC_check: (
                lambda: self.universal_update(
                    'potato_PC',
                    self.ui.potatoPC_check.isChecked(),
                    "Potato PC {VALUE}.",
                    "checkbox"
                ),
                lambda: self.universal_setter(
                    self.ui.potatoPC_check,
                    self.config.potato_PC,
                    "Potato PC {VALUE}.",
                    "checkbox"
                )
            ),
        }
        for checkbox, (handler, operation) in checkboxes.items():
            checkbox.stateChanged.connect(handler)
            operation()
        self.config.log('mainWindow', 'set_checkboxes', "Checkboxes set.")

    # Textboxes definition
    def set_textboxes(self):
        paths = {
            self.ui.audio_path_editline: lambda: self.universal_update(
                'rendering_paths.audio',
                self.ui.audio_path_editline.text(),
                "Audio path updated to: {VALUE}.",
                "textbox"
            ),
            self.ui.raw_path_editline: lambda: self.universal_update(
                'rendering_paths.raw',
                self.ui.raw_path_editline.text(),
                "Raw path updated to: {VALUE}.",
                "textbox"
            ),
            self.ui.subtitle_path_editline: lambda: self.universal_update(
                'rendering_paths.sub',
                self.ui.subtitle_path_editline.text(),
                "Subtitle path updated to: {VALUE}.",
                "textbox"
            ),
            self.ui.episode_line: lambda: self.universal_update(
                'build_settings.episode_name',
                self.ui.episode_line.text(),
                "Episode name updated to: {VALUE}.",
                "textbox",
                self.update_render_paths
            ),
            self.ui.softsub_path_editline: lambda: self.universal_update(
                'main_paths.softsub',
                self.ui.softsub_path_editline.text(),
                None,
                "textbox",
                self.soft_path_constructor
            ),
        }

        for textbox, handler in paths.items():
            textbox.textChanged.connect(handler)

        self.config.log('mainWindow', 'set_textboxes', "Textboxes set.")

    # Comboboxes definition
    def set_comboboxes(self):
        comboboxes = {
            self.ui.render_mode_box: lambda: self.universal_update(
                'build_settings.build_state',
                self.ui.render_mode_box.currentIndex(),
                "Build state updated to: {VALUE}.".format(
                    VALUE=self.ui.render_mode_box.currentText()
                ),
                "combobox",
                self.lock_mode
            ),
            self.ui.logo_box: lambda: self.universal_update(
                'build_settings.logo_state',
                self.ui.logo_box.currentIndex(),
                "Logo state updated to: {VALUE}.".format(
                    VALUE=self.ui.logo_box.currentText()
                ),
                "combobox",
                None
            ),
            self.ui.nvenc_box: lambda: self.universal_update(
                'build_settings.nvenc_state',
                self.ui.nvenc_box.currentIndex(),
                "NVENC state updated to: {VALUE}.".format(
                    VALUE=self.ui.nvenc_box.currentText()
                ),
                "combobox",
                None
            ),
        }

        for combobox, handler in comboboxes.items():
            combobox.currentIndexChanged.connect(handler)

        self.ui.render_mode_box.setCurrentIndex(self.config.build_settings.build_state)
        self.ui.logo_box.setCurrentIndex(self.config.build_settings.logo_state)
        self.ui.nvenc_box.setCurrentIndex(self.config.build_settings.nvenc_state)
        if not self.config.ffmpeg.nvenc:
            self.ui.nvenc_box.setCurrentIndex(3)
            self.ui.nvenc_box.hide()
            self.ui.nvenc_label.setText('NVENC: Не доступен')

        self.config.log('mainWindow', 'set_comboboxes', "Comboboxes set.")

    def open_file(self, filename):
        if self.config.pc_info.is_windows():
            os.startfile(filename)
            return

        opener = "open" if self.config.pc_info.Platform == "darwin" else "xdg-open"
        subprocess.call([opener, filename])

    # Open hardsub directory
    def open_hardsub(self):
        if os.path.exists(self.config.main_paths.hardsub):
            self.open_file(self.config.main_paths.hardsub)
        else:
            self.coding_error('hardsub_folder')
        self.config.log('mainWindow', 'open_hardsub', "Hardsub folder opened.")

    def open_logsdir(self):
        if os.path.exists(self.config.main_paths.logs):
            self.open_file(self.config.main_paths.logs)
        else:
            self.coding_error('logs_folder')
        self.config.log('mainWindow', 'open_logsdir', "Logs folder opened.")

    # Softsub saving path
    def soft_folder_path(self):
        self.config.main_paths.softsub = QtWidgets.QFileDialog.getExistingDirectory(self, 'Куда пихать софт?')
        self.ui.softsub_path_editline.setText(self.config.main_paths.softsub)
        self.config.log('mainWindow', 'soft_folder_path', f"Softsub path updated to: {self.config.main_paths.softsub}")

    # Raw video choose
    def raw_folder_path(self):
        self._ui_paths['raw'], _ = QtWidgets.QFileDialog.getOpenFileName(self, "Где брать равку?", "",
                                                            "ALL (*.mkv *.mp4 *.avi)")
        self.ui.raw_path_editline.setText(self._ui_paths['raw'])
        self.config.log('mainWindow', 'raw_folder_path', f"Raw path updated to: {self._ui_paths['raw']}")

    # Sound file choose
    def sound_folder_path(self):
        self._ui_paths['audio'], _ = QtWidgets.QFileDialog.getOpenFileName(self, "Где брать звук?", "",
                                                            "All(*.wav *.flac *.aac *.m4a *.mka)")
        self.ui.audio_path_editline.setText(self._ui_paths['audio'])
        self.config.log('mainWindow', 'sound_folder_path', f"Sound path updated to: {self._ui_paths['audio']}")

    # Subtitle choose
    def sub_folder_path(self):
        self._ui_paths['sub'], _ = QtWidgets.QFileDialog.getOpenFileName(self, "Где брать надписи?", "",
                                                            "Хуй (*.ass *.srt)")
        self.ui.subtitle_path_editline.setText(self._ui_paths['sub'])
        self.config.log('mainWindow', 'sub_folder_path', f"Subtitle path updated to: {self._ui_paths['sub']}")

    # Coding Errors
    def coding_error(self, error_type):
        error_messages = {
            'softsub': ("Выбери правильно куда сохранять софтсаб!", self.soft_folder_path),
            'subtitle': ("Выбери существующий путь к файлу субтитров!", self.sub_folder_path),
            'raw': ("Выбери существующий путь к равке!", self.raw_folder_path),
            'sound': ("Выбери существующий путь к дорожке звука!", self.sound_folder_path),
            'name': ("Напиши корректное имя релиза!", None),
            'hardsub_folder': ("НАХУЯ ТЫ ПАПКИ УДАЛЯЕШЬ?!", None),
            'stop': ("Зачем остановил?!", None),
            'logs_folder' : ("НАХУЯ ТЫ ПАПКИ УДАЛЯЕШЬ?!", None),
        }

        self.ui.app_state_label.setText("МЕГАПЛОХ!")
        msg = QMessageBox()
        msg.setWindowTitle("Чел ты...")
        msg.setIcon(QMessageBox.Warning)

        if error_type in error_messages:
            message, action = error_messages[error_type]
            msg.setText(message)
            if action:
                msg.setStandardButtons(QMessageBox.Open)
                msg.buttonClicked.connect(action)
            else:
                msg.setStandardButtons(QMessageBox.Ok)
            if error_type == 'hardsub_folder':
                os.mkdir('HARDSUB')

        msg.exec_()
        self.config.log('mainWindow', 'coding_error', f"Coding error: {error_type}")

    # Progress updater
    def frame_update(self, frame):
        self.config.log('mainWindow', 'frame_update', f"Frame updated: {frame}")
        self.ui.render_progress_bar.setValue(int(frame))

    # Set progressbar maximum
    def time_update(self, time):
        self.config.log('mainWindow', 'time_update', f"Time updated: {time}")
        self.ui.render_progress_bar.setMaximum(math.ceil(time))

    # State updater
    def state_update(self, state):
        self.config.log('mainWindow', 'state_update', f"State updated: {state}")
        self.ui.app_state_label.setText(state)

    def elapsed_time_update(self, time):
        self.config.log('mainWindow', 'elapsed_time_update', f"Elapsed time updated: {time}")
        self.ui.elapsed_time_label.setText(time)

    def _create_render_paths(self) -> RenderPaths:
        """Factory: create RenderPaths from current UI state."""
        return RenderPaths.from_ui_state(
            raw_path=self._ui_paths['raw'],
            audio_path=self._ui_paths['audio'],
            sub_path=self._ui_paths['sub'],
            episode_name=self.config.build_settings.episode_name,
            softsub_dir=self.config.main_paths.softsub,
            hardsub_dir=self.config.main_paths.hardsub,
        )

    def _validate_before_render(self) -> bool:
        """Validate paths before starting render. Returns True if valid."""
        try:
            paths = self._create_render_paths()
            errors = paths.validate()

            if errors:
                # Show errors to user
                error_msg = "\n".join(errors)
                QtWidgets.QMessageBox.critical(self, "Validation Error", error_msg)
                self.config.log('mainWindow', '_validate_before_render', f"Validation failed: {error_msg}")
                return False

            self.config.log('mainWindow', '_validate_before_render', "Validation passed")
            return True
        except Exception as e:
            error_msg = f"Error validating paths: {str(e)}"
            QtWidgets.QMessageBox.critical(self, "Error", error_msg)
            self.config.log('mainWindow', '_validate_before_render', error_msg)
            return False

    # Thread start with ffmpeg
    def ffmpeg_thread(self):
        # Directory checks
        if not os.path.exists(self.config.main_paths.hardsub):
            self.coding_error('hardsub_folder')
            return

        if not os.path.exists(self.config.main_paths.softsub) and self.config.build_settings.build_state in [0, 1, 4]:
            self.coding_error('softsub')
            return

        # Episode name validation
        if not re.match(r'^[a-zA-Zа-яА-Я0-9 _.\-\[\]!(),@~]+$', self.config.build_settings.episode_name):
            self.coding_error('name')
            return

        self.ui.app_state_label.setText("Работаю....(наверное)")
        self.ui.render_progress_bar.setValue(0)

        # Validate input paths using new centralized validation
        if not self._validate_before_render():
            return

        # Create validated, immutable paths
        paths = self._create_render_paths()

        self.config.log('mainWindow', 'ffmpeg_thread', "Starting ffmpeg with validated paths...")
        self.threadMain = ThreadClassRender(self.config, runner=self.runner, paths=paths)
        self.threadMain.finished.connect(self.finished)
        self.threadMain.frame_upd.connect(self.frame_update)
        self.threadMain.time_upd.connect(self.time_update)
        self.threadMain.state_upd.connect(self.state_update)
        self.threadMain.elapsed_time_upd.connect(self.elapsed_time_update)
        self.locker(True)
        self.ui.render_start_button.hide()
        self.ui.render_stop_button.show()
        self.threadMain.start()

    # Kill ffmpeg process
    def proc_kill(self):
        self.finish_message = True
        if hasattr(self, 'threadMain') and self.threadMain and self.threadMain.runner:
            # Use ProcessRunner for safe, targeted kill
            self.threadMain.runner.kill_ffmpeg()
            self.config.log('mainWindow', 'proc_kill', "Killed ffmpeg process via ProcessRunner")
        else:
            # Fallback to old method if ProcessRunner not available
            if self.config.pc_info.is_windows():
                subprocess.run('taskkill /f /im ffmpeg.exe', shell=True)
            else:
                subprocess.run('kill $(pgrep ffmpeg)', shell=True)
            self.config.log('mainWindow', 'proc_kill', "Killed ffmpeg process (fallback method)")

    # After coding
    def finished(self):
        os.chdir(self.config.main_paths.cwd)
        self.ui.render_start_button.show()
        self.ui.render_stop_button.hide()

        if self.finish_message:
            self.coding_error('stop')
            self.finish_message = False
        else:
            self.state_update("Все готово!")
            self.elapsed_time_update('')
            QApplication.beep()
        self.ui.elapsed_time_label.setText('')
        self.ui.render_progress_bar.setValue(0)
        self.locker(False)
        self.config.log('mainWindow', 'finished', "Coding finished")

    # Blocking strings and buttons while coding
    def locker(self, lock_value):
        for item in self.base:
            item.setDisabled(lock_value)

        tabs = [self.ui.folder_tab, self.ui.settings_tab, self.ui.whats_new_tab, self.ui.dev_tab]
        for tab in tabs:
            tab.setDisabled(lock_value)

        self.ui.render_stop_button.setDisabled(not lock_value)
        self.lock_mode()
        self.config.log('mainWindow', 'locker', "UI locked")

    # Queue event handlers
    def on_job_started(self, job_id: str):
        """Handle job started event from queue processor.

        Args:
            job_id: ID of the job that started
        """
        self.config.log('mainWindow', 'on_job_started', f"Job started: {job_id}")
        # TODO: Update UI to show job is running
        self.refresh_queue_display()

    def on_job_completed(self, job_id: str):
        """Handle job completed event from queue processor.

        Args:
            job_id: ID of the job that completed
        """
        self.config.log('mainWindow', 'on_job_completed', f"Job completed: {job_id}")
        # TODO: Update UI to show job completion
        self.refresh_queue_display()

    def on_job_failed(self, job_id: str, error_message: str):
        """Handle job failed event from queue processor.

        Args:
            job_id: ID of the job that failed
            error_message: Error message describing the failure
        """
        self.config.log('mainWindow', 'on_job_failed', f"Job failed: {job_id} - {error_message}")
        # TODO: Show error to user
        self.refresh_queue_display()

    def on_job_cancelled(self, job_id: str):
        """Handle job cancelled event from queue processor.

        Args:
            job_id: ID of the job that was cancelled
        """
        self.config.log('mainWindow', 'on_job_cancelled', f"Job cancelled: {job_id}")
        # TODO: Update UI to show job cancellation
        self.refresh_queue_display()

    def on_queue_finished(self):
        """Handle queue finished event from queue processor.

        Emitted when all jobs in the queue have been processed.
        """
        self.config.log('mainWindow', 'on_queue_finished', "Queue processing finished")
        # TODO: Update UI to show queue is finished
        self.refresh_queue_display()

    def on_move_up_requested(self, job_id: str):
        """Handle move up request from queue widget.

        Args:
            job_id: ID of the job to move up
        """
        self.config.log('mainWindow', 'on_move_up_requested', f"Move up requested: {job_id}")
        if self.job_queue.move_up(job_id):
            self.refresh_queue_display()
        else:
            self.config.log('mainWindow', 'on_move_up_requested', f"Failed to move up job: {job_id}")

    def on_move_down_requested(self, job_id: str):
        """Handle move down request from queue widget.

        Args:
            job_id: ID of the job to move down
        """
        self.config.log('mainWindow', 'on_move_down_requested', f"Move down requested: {job_id}")
        if self.job_queue.move_down(job_id):
            self.refresh_queue_display()
        else:
            self.config.log('mainWindow', 'on_move_down_requested', f"Failed to move down job: {job_id}")

    def on_remove_requested(self, job_id: str):
        """Handle remove request from queue widget.

        Args:
            job_id: ID of the job to remove
        """
        self.config.log('mainWindow', 'on_remove_requested', f"Remove requested: {job_id}")
        if self.job_queue.remove(job_id):
            self.refresh_queue_display()
        else:
            self.config.log('mainWindow', 'on_remove_requested', f"Failed to remove job: {job_id}")

    def on_stop_requested(self, job_id: str):
        """Handle stop request from queue widget.

        Args:
            job_id: ID of the job to stop
        """
        self.config.log('mainWindow', 'on_stop_requested', f"Stop requested: {job_id}")
        # TODO: Implement job cancellation
        self.queue_processor.cancel_current_job()

    def on_clear_completed_requested(self):
        """Handle clear completed request from queue widget.

        Removes all completed jobs from the queue.
        """
        self.config.log('mainWindow', 'on_clear_completed_requested', "Clear completed requested")
        self.job_queue.clear_completed()
        self.refresh_queue_display()

    def refresh_queue_display(self):
        """Refresh the queue widget to show current queue state."""
        jobs = self.job_queue.get_all_jobs()
        self.queue_widget.update_jobs(jobs)
