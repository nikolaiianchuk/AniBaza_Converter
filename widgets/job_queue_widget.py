"""Job queue UI widgets - display and control render queue."""

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
)

from models.job_queue import QueuedJob
from models.enums import JobStatus


class JobListItem(QWidget):
    """Widget displaying a single job in the queue.

    Shows:
    - Status icon (waiting/running/completed/failed/cancelled)
    - Episode name
    - Action buttons based on state:
        - WAITING: move up/down, remove
        - RUNNING: stop
        - COMPLETED/FAILED/CANCELLED: remove

    Signals:
        move_up_requested(str): Emitted when move up clicked, passes job ID
        move_down_requested(str): Emitted when move down clicked, passes job ID
        remove_requested(str): Emitted when remove clicked, passes job ID
        stop_requested(str): Emitted when stop clicked, passes job ID
    """

    # Signals for user actions
    move_up_requested = pyqtSignal(str)
    move_down_requested = pyqtSignal(str)
    remove_requested = pyqtSignal(str)
    stop_requested = pyqtSignal(str)

    # Status icons/text
    STATUS_ICONS = {
        JobStatus.WAITING: "⏳ WAITING",
        JobStatus.RUNNING: "▶ RUNNING",
        JobStatus.COMPLETED: "✓ COMPLETED",
        JobStatus.FAILED: "✗ FAILED",
        JobStatus.CANCELLED: "⊗ CANCELLED",
    }

    def __init__(self, queued_job: QueuedJob, parent=None):
        """Initialize job list item widget.

        Args:
            queued_job: QueuedJob to display
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        self.queued_job = queued_job
        self.job_id = queued_job.id

        # Initialize attributes that may not exist depending on status
        self.move_up_button = None
        self.move_down_button = None
        self.remove_button = None
        self.stop_button = None

        self._setup_ui()

    def _setup_ui(self):
        """Build the widget UI based on job status."""
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(10)

        # Status icon/label
        self.status_label = QLabel(self.STATUS_ICONS.get(
            self.queued_job.status,
            str(self.queued_job.status)
        ))
        layout.addWidget(self.status_label)

        # Episode name label
        label_text = self.queued_job.job.episode_name

        # Add error message for failed jobs
        if self.queued_job.status == JobStatus.FAILED and self.queued_job.error_message:
            tooltip_text = f"Error: {self.queued_job.error_message}"
        else:
            tooltip_text = ""

        self.label = QLabel(label_text)
        if tooltip_text:
            self.label.setToolTip(tooltip_text)
        layout.addWidget(self.label)

        # Spacer to push buttons to the right
        layout.addStretch()

        # Add buttons based on job status
        if self.queued_job.status == JobStatus.WAITING:
            self._add_waiting_buttons(layout)
        elif self.queued_job.status == JobStatus.RUNNING:
            self._add_running_buttons(layout)
        elif self.queued_job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
            self._add_finished_buttons(layout)

        self.setLayout(layout)

    def _add_waiting_buttons(self, layout: QHBoxLayout):
        """Add buttons for WAITING jobs: move up, move down, remove.

        Args:
            layout: Layout to add buttons to
        """
        # Move up button
        self.move_up_button = QPushButton("↑")
        self.move_up_button.setFixedSize(30, 30)
        self.move_up_button.setToolTip("Move up in queue")
        self.move_up_button.clicked.connect(lambda: self.move_up_requested.emit(self.job_id))
        layout.addWidget(self.move_up_button)

        # Move down button
        self.move_down_button = QPushButton("↓")
        self.move_down_button.setFixedSize(30, 30)
        self.move_down_button.setToolTip("Move down in queue")
        self.move_down_button.clicked.connect(lambda: self.move_down_requested.emit(self.job_id))
        layout.addWidget(self.move_down_button)

        # Remove button
        self.remove_button = QPushButton("✕")
        self.remove_button.setFixedSize(30, 30)
        self.remove_button.setToolTip("Remove from queue")
        self.remove_button.clicked.connect(lambda: self.remove_requested.emit(self.job_id))
        layout.addWidget(self.remove_button)

    def _add_running_buttons(self, layout: QHBoxLayout):
        """Add buttons for RUNNING jobs: stop only.

        Args:
            layout: Layout to add buttons to
        """
        # Stop button
        self.stop_button = QPushButton("Stop")
        self.stop_button.setFixedWidth(60)
        self.stop_button.setToolTip("Stop running job")
        self.stop_button.clicked.connect(lambda: self.stop_requested.emit(self.job_id))
        layout.addWidget(self.stop_button)

    def _add_finished_buttons(self, layout: QHBoxLayout):
        """Add buttons for finished jobs (COMPLETED/FAILED/CANCELLED): remove only.

        Args:
            layout: Layout to add buttons to
        """
        # Remove button
        self.remove_button = QPushButton("✕")
        self.remove_button.setFixedSize(30, 30)
        self.remove_button.setToolTip("Remove from queue")
        self.remove_button.clicked.connect(lambda: self.remove_requested.emit(self.job_id))
        layout.addWidget(self.remove_button)


class JobQueueWidget(QWidget):
    """Container widget displaying job queue with controls.

    Shows:
    - QListWidget with all queued jobs (as JobListItem widgets)
    - Clear Completed button to remove finished jobs

    Signals:
        move_up_requested(str): Emitted when job move up clicked, passes job ID
        move_down_requested(str): Emitted when job move down clicked, passes job ID
        remove_requested(str): Emitted when job remove clicked, passes job ID
        stop_requested(str): Emitted when job stop clicked, passes job ID
        clear_completed_requested(): Emitted when clear completed button clicked
    """

    # Signals propagated from JobListItem widgets
    move_up_requested = pyqtSignal(str)
    move_down_requested = pyqtSignal(str)
    remove_requested = pyqtSignal(str)
    stop_requested = pyqtSignal(str)

    # Signal from clear button
    clear_completed_requested = pyqtSignal()

    def __init__(self, parent=None):
        """Initialize job queue widget.

        Args:
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Build the widget UI with list and controls."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Job list widget
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        # Clear completed button
        self.clear_completed_button = QPushButton("Clear Completed")
        self.clear_completed_button.setToolTip("Remove all completed jobs from queue")
        self.clear_completed_button.clicked.connect(self.clear_completed_requested.emit)
        layout.addWidget(self.clear_completed_button)

        self.setLayout(layout)

    def update_jobs(self, jobs: list[QueuedJob]):
        """Update displayed job list.

        Clears list and recreates all JobListItem widgets from provided jobs.
        Connects JobListItem signals to propagate through this widget.

        Args:
            jobs: List of QueuedJob objects to display
        """
        # Clear existing items
        self.list_widget.clear()

        # Add each job as a JobListItem
        for queued_job in jobs:
            # Create JobListItem widget
            job_item_widget = JobListItem(queued_job)

            # Connect signals to propagate
            job_item_widget.move_up_requested.connect(self.move_up_requested.emit)
            job_item_widget.move_down_requested.connect(self.move_down_requested.emit)
            job_item_widget.remove_requested.connect(self.remove_requested.emit)
            job_item_widget.stop_requested.connect(self.stop_requested.emit)

            # Create list item and set widget
            list_item = QListWidgetItem(self.list_widget)
            list_item.setSizeHint(job_item_widget.sizeHint())
            self.list_widget.addItem(list_item)
            self.list_widget.setItemWidget(list_item, job_item_widget)
