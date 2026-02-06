"""Queue processor thread - sequential job execution.

This thread processes jobs from the JobQueue sequentially.
Run loop implementation will be added in Task 10.
"""

from typing import Optional
from PyQt5.QtCore import QThread, pyqtSignal

from models.job_queue import JobQueue


class QueueProcessor(QThread):
    """QThread that processes jobs from queue sequentially.

    Responsibilities:
    - Process jobs one at a time from JobQueue
    - Emit signals for job lifecycle events
    - Support cancellation of current job
    - Support pause/resume functionality

    Signals:
        job_started(str): Emitted when job starts (job_id)
        job_completed(str): Emitted when job completes successfully (job_id)
        job_failed(str, str): Emitted when job fails (job_id, error_message)
        job_cancelled(str): Emitted when job is cancelled (job_id)
        queue_finished(): Emitted when all jobs are processed
    """

    # Signals for job lifecycle events
    job_started = pyqtSignal(str)  # job_id
    job_completed = pyqtSignal(str)  # job_id
    job_failed = pyqtSignal(str, str)  # job_id, error_message
    job_cancelled = pyqtSignal(str)  # job_id
    queue_finished = pyqtSignal()  # no arguments

    def __init__(self, queue: JobQueue):
        """Initialize QueueProcessor.

        Args:
            queue: JobQueue instance to process jobs from
        """
        super().__init__()
        self.queue = queue
        self.current_job_id: Optional[str] = None
        self.cancelled: bool = False

    def cancel_current_job(self) -> None:
        """Cancel the currently running job.

        Sets the cancelled flag to True. The run loop (Task 10)
        will check this flag and abort the current job.
        """
        self.cancelled = True

    def resume(self) -> None:
        """Resume processing after cancellation.

        Clears the cancelled flag, allowing queue processing to continue.
        """
        self.cancelled = False

    def run(self) -> None:
        """Main thread loop for processing jobs.

        Stub implementation for Task 9.
        Full implementation will be added in Task 10.
        """
        # Task 10 will implement:
        # - Loop through queue.get_next_waiting()
        # - Set current_job_id and emit job_started
        # - Execute job (create RenderThread, connect signals)
        # - Update job status based on result
        # - Emit appropriate completion signals
        # - Check cancelled flag between jobs
        # - Emit queue_finished when done
        pass
