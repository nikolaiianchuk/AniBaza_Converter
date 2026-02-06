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
