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

    # Forward signals from RenderThread for progress updates
    frame_upd = pyqtSignal(object)  # Frame progress
    time_upd = pyqtSignal(object)  # Time progress
    state_upd = pyqtSignal(object)  # State updates
    elapsed_time_upd = pyqtSignal(object)  # Elapsed time

    def __init__(self, queue: JobQueue, config=None, runner=None):
        """Initialize QueueProcessor.

        Args:
            queue: JobQueue instance to process jobs from
            config: Application config (required for RenderThread)
            runner: ProcessRunner for ffmpeg execution
        """
        super().__init__()
        self.queue = queue
        self.config = config
        self.runner = runner
        self.current_job_id: Optional[str] = None
        self.current_render_thread: Optional['ThreadClassRender'] = None
        self.cancelled: bool = False

    def cancel_current_job(self) -> None:
        """Cancel the currently running job.

        Stops the current RenderThread and sets the cancelled flag.
        """
        self.cancelled = True
        if self.current_render_thread:
            self.current_render_thread.stop()  # Stop the actual ffmpeg process

    def resume(self) -> None:
        """Resume processing after cancellation.

        Clears the cancelled flag, allowing queue processing to continue.
        """
        self.cancelled = False

    def run(self) -> None:
        """Main thread loop for processing jobs.

        Processes jobs sequentially from the queue:
        1. Get next waiting job
        2. Create RenderThread for the job
        3. Execute and wait for completion
        4. Update job status based on result
        5. Emit appropriate signals
        6. Handle cancellation between jobs
        7. Emit queue_finished when all jobs are done
        """
        from threads.RenderThread import ThreadClassRender
        from models.enums import JobStatus

        # Reset cancelled flag at start (important when restarting after stop)
        self.cancelled = False

        while True:
            # Check if cancelled before processing next job
            if self.cancelled:
                break

            # Get next waiting job
            queued_job = self.queue.get_next_waiting()
            if queued_job is None:
                # No more waiting jobs
                break

            # Set current job and update status to RUNNING
            self.current_job_id = queued_job.id
            self.queue.update_status(queued_job.id, JobStatus.RUNNING)
            self.job_started.emit(queued_job.id)

            try:
                # Check if cancelled after starting job
                if self.cancelled:
                    # Mark job as cancelled
                    self.queue.update_status(queued_job.id, JobStatus.CANCELLED)
                    self.job_cancelled.emit(queued_job.id)
                    self.current_job_id = None
                    break

                # Create and run RenderThread for this job
                self.current_render_thread = ThreadClassRender(
                    config=self.config,
                    runner=self.runner,
                    paths=queued_job.job.paths
                )

                # Connect RenderThread signals to forward progress updates
                self.current_render_thread.frame_upd.connect(self.frame_upd.emit)
                self.current_render_thread.time_upd.connect(self.time_upd.emit)
                self.current_render_thread.state_upd.connect(self.state_upd.emit)
                self.current_render_thread.elapsed_time_upd.connect(self.elapsed_time_upd.emit)

                # Run the render thread synchronously
                self.current_render_thread.run()

                # Check if job was cancelled during execution
                if self.current_render_thread._cancelled:
                    self.queue.update_status(queued_job.id, JobStatus.CANCELLED)
                    self.job_cancelled.emit(queued_job.id)
                else:
                    # Job completed successfully
                    self.queue.update_status(queued_job.id, JobStatus.COMPLETED)
                    self.job_completed.emit(queued_job.id)

            except Exception as e:
                # Job failed
                error_message = str(e)
                self.queue.update_status(
                    queued_job.id,
                    JobStatus.FAILED,
                    error_message=error_message
                )
                self.job_failed.emit(queued_job.id, error_message)

            finally:
                # Clear current job and thread reference
                self.current_job_id = None
                self.current_render_thread = None

        # All jobs processed
        self.queue_finished.emit()
