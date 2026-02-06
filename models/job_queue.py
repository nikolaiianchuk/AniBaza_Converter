"""Job queue management - thread-safe queue operations."""

import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from models.enums import JobStatus
from models.job import RenderJob


@dataclass
class QueuedJob:
    """Wrapper around RenderJob with queue metadata.

    Tracks job state, ID, and error information.
    Mutable to allow status updates during processing.
    """
    job: RenderJob
    id: str
    status: JobStatus = JobStatus.WAITING
    created_at: datetime = field(default_factory=datetime.now)
    error_message: Optional[str] = None


class JobQueue:
    """Thread-safe job queue manager.

    Manages list of queued jobs with operations:
    - Add jobs with unique IDs
    - Remove/reorder waiting jobs
    - Update job status
    - Get next waiting job for processing

    All operations are thread-safe using a lock.
    """

    def __init__(self):
        self._jobs: list[QueuedJob] = []
        self._lock = threading.Lock()

    def add(self, job: RenderJob) -> str:
        """Add job to queue, return unique ID.

        Args:
            job: RenderJob to queue

        Returns:
            Unique job ID (UUID)
        """
        with self._lock:
            job_id = str(uuid.uuid4())
            queued = QueuedJob(
                job=job,
                id=job_id,
                status=JobStatus.WAITING
            )
            self._jobs.append(queued)
            return job_id

    def get_all_jobs(self) -> list[QueuedJob]:
        """Get copy of all jobs for display.

        Returns:
            List of all queued jobs (copy to prevent external modification)
        """
        with self._lock:
            return self._jobs.copy()
