# Render Job Queue Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add job queue functionality allowing users to configure multiple render jobs before processing them sequentially.

**Architecture:** Create JobQueue model with thread-safe operations, QueueProcessor thread wrapping existing RenderThread, and JobQueueWidget for UI display. Integrate with MainWindow by repurposing existing Start/Stop buttons to work with queue.

**Tech Stack:** PyQt5, Python dataclasses, threading.Lock, pytest-qt

---

## Task 1: Add JobStatus Enum

**Files:**
- Modify: `models/enums.py`
- Test: `tests/test_enums.py`

**Step 1: Write the failing test**

Add to `tests/test_enums.py`:

```python
def test_job_status_values():
    """JobStatus enum has all required states."""
    from models.enums import JobStatus

    assert JobStatus.WAITING.value == 0
    assert JobStatus.RUNNING.value == 1
    assert JobStatus.COMPLETED.value == 2
    assert JobStatus.FAILED.value == 3
    assert JobStatus.CANCELLED.value == 4

def test_job_status_membership():
    """JobStatus can be used in membership checks."""
    from models.enums import JobStatus

    status = JobStatus.WAITING
    assert status in [JobStatus.WAITING, JobStatus.RUNNING]
    assert status not in [JobStatus.COMPLETED, JobStatus.FAILED]
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_enums.py::test_job_status_values -v`

Expected: FAIL with "cannot import name 'JobStatus'"

**Step 3: Add JobStatus enum**

Add to `models/enums.py`:

```python
class JobStatus(IntEnum):
    """Job processing states."""
    WAITING = 0
    RUNNING = 1
    COMPLETED = 2
    FAILED = 3
    CANCELLED = 4
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_enums.py -v`

Expected: All tests PASS

**Step 5: Commit**

```bash
git add models/enums.py tests/test_enums.py
git commit -m "feat: add JobStatus enum for queue states

Add WAITING, RUNNING, COMPLETED, FAILED, CANCELLED states.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 2: Create JobQueue Model

**Files:**
- Create: `models/job_queue.py`
- Create: `tests/test_job_queue.py`

**Step 1: Write failing tests for QueuedJob**

Create `tests/test_job_queue.py`:

```python
"""Tests for models/job_queue.py - job queue management."""

import pytest
from datetime import datetime
from unittest.mock import Mock

from models.job_queue import QueuedJob, JobQueue
from models.enums import JobStatus


class TestQueuedJob:
    """Test QueuedJob dataclass."""

    def test_queued_job_creation(self):
        """QueuedJob wraps RenderJob with metadata."""
        mock_job = Mock()

        queued = QueuedJob(
            job=mock_job,
            id="test-123",
            status=JobStatus.WAITING
        )

        assert queued.job == mock_job
        assert queued.id == "test-123"
        assert queued.status == JobStatus.WAITING
        assert queued.error_message is None
        assert isinstance(queued.created_at, datetime)

    def test_queued_job_with_error(self):
        """QueuedJob can store error message."""
        mock_job = Mock()

        queued = QueuedJob(
            job=mock_job,
            id="test-456",
            status=JobStatus.FAILED,
            error_message="FFmpeg failed"
        )

        assert queued.status == JobStatus.FAILED
        assert queued.error_message == "FFmpeg failed"
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_job_queue.py::TestQueuedJob -v`

Expected: FAIL with "No module named 'models.job_queue'"

**Step 3: Create QueuedJob dataclass**

Create `models/job_queue.py`:

```python
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
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_job_queue.py::TestQueuedJob -v`

Expected: All tests PASS

**Step 5: Commit**

```bash
git add models/job_queue.py tests/test_job_queue.py
git commit -m "feat: add QueuedJob dataclass

Wraps RenderJob with queue metadata (id, status, error).

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 3: Implement JobQueue.add()

**Files:**
- Modify: `models/job_queue.py`
- Modify: `tests/test_job_queue.py`

**Step 1: Write failing test**

Add to `tests/test_job_queue.py`:

```python
class TestJobQueue:
    """Test JobQueue operations."""

    def test_add_job_returns_id(self):
        """Adding job returns unique ID."""
        queue = JobQueue()
        mock_job = Mock()

        job_id = queue.add(mock_job)

        assert isinstance(job_id, str)
        assert len(job_id) == 36  # UUID format

    def test_add_multiple_jobs(self):
        """Adding multiple jobs creates unique IDs."""
        queue = JobQueue()

        id1 = queue.add(Mock())
        id2 = queue.add(Mock())

        assert id1 != id2
        assert len(queue.get_all_jobs()) == 2

    def test_added_jobs_are_waiting(self):
        """Newly added jobs have WAITING status."""
        queue = JobQueue()
        mock_job = Mock()

        job_id = queue.add(mock_job)
        jobs = queue.get_all_jobs()

        assert len(jobs) == 1
        assert jobs[0].id == job_id
        assert jobs[0].status == JobStatus.WAITING
        assert jobs[0].job == mock_job
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_job_queue.py::TestJobQueue::test_add_job_returns_id -v`

Expected: FAIL with "JobQueue not defined"

**Step 3: Implement JobQueue class with add()**

Add to `models/job_queue.py`:

```python
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
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_job_queue.py::TestJobQueue -v`

Expected: All tests PASS

**Step 5: Commit**

```bash
git add models/job_queue.py tests/test_job_queue.py
git commit -m "feat: implement JobQueue.add() with thread safety

Add jobs to queue with unique UUID, return ID.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 4: Implement JobQueue.remove()

**Files:**
- Modify: `models/job_queue.py`
- Modify: `tests/test_job_queue.py`

**Step 1: Write failing tests**

Add to `tests/test_job_queue.py`:

```python
def test_remove_waiting_job_succeeds(self):
    """Can remove job with WAITING status."""
    queue = JobQueue()
    job_id = queue.add(Mock())

    result = queue.remove(job_id)

    assert result is True
    assert len(queue.get_all_jobs()) == 0

def test_remove_nonexistent_job_fails(self):
    """Removing nonexistent job returns False."""
    queue = JobQueue()

    result = queue.remove("fake-id")

    assert result is False

def test_remove_running_job_fails(self):
    """Cannot remove job with RUNNING status."""
    queue = JobQueue()
    job_id = queue.add(Mock())
    queue.update_status(job_id, JobStatus.RUNNING)

    result = queue.remove(job_id)

    assert result is False
    assert len(queue.get_all_jobs()) == 1

def test_remove_completed_job_succeeds(self):
    """Can remove job with COMPLETED status."""
    queue = JobQueue()
    job_id = queue.add(Mock())
    queue.update_status(job_id, JobStatus.COMPLETED)

    result = queue.remove(job_id)

    assert result is True
    assert len(queue.get_all_jobs()) == 0
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_job_queue.py::TestJobQueue::test_remove_waiting_job_succeeds -v`

Expected: FAIL with "'JobQueue' object has no attribute 'remove'"

**Step 3: Implement remove() method**

Add to `models/job_queue.py` in JobQueue class:

```python
def remove(self, job_id: str) -> bool:
    """Remove job from queue if not RUNNING.

    Args:
        job_id: ID of job to remove

    Returns:
        True if removed, False if not found or currently running
    """
    with self._lock:
        for i, queued_job in enumerate(self._jobs):
            if queued_job.id == job_id:
                # Cannot remove running jobs
                if queued_job.status == JobStatus.RUNNING:
                    return False
                self._jobs.pop(i)
                return True
        return False
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_job_queue.py::TestJobQueue -v`

Expected: All tests PASS

**Step 5: Commit**

```bash
git add models/job_queue.py tests/test_job_queue.py
git commit -m "feat: implement JobQueue.remove() with running protection

Can remove jobs except those currently RUNNING.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 5: Implement JobQueue Reordering (move_up/move_down)

**Files:**
- Modify: `models/job_queue.py`
- Modify: `tests/test_job_queue.py`

**Step 1: Write failing tests**

Add to `tests/test_job_queue.py`:

```python
def test_move_up_waiting_job(self):
    """Can move WAITING job up in queue."""
    queue = JobQueue()
    id1 = queue.add(Mock(episode_name="Ep 01"))
    id2 = queue.add(Mock(episode_name="Ep 02"))
    id3 = queue.add(Mock(episode_name="Ep 03"))

    result = queue.move_up(id2)

    assert result is True
    jobs = queue.get_all_jobs()
    assert jobs[0].id == id2
    assert jobs[1].id == id1
    assert jobs[2].id == id3

def test_move_up_first_job_noop(self):
    """Moving first job up returns False."""
    queue = JobQueue()
    id1 = queue.add(Mock())
    queue.add(Mock())

    result = queue.move_up(id1)

    assert result is False

def test_move_up_running_job_fails(self):
    """Cannot move RUNNING job."""
    queue = JobQueue()
    id1 = queue.add(Mock())
    id2 = queue.add(Mock())
    queue.update_status(id2, JobStatus.RUNNING)

    result = queue.move_up(id2)

    assert result is False

def test_move_down_waiting_job(self):
    """Can move WAITING job down in queue."""
    queue = JobQueue()
    id1 = queue.add(Mock())
    id2 = queue.add(Mock())
    id3 = queue.add(Mock())

    result = queue.move_down(id1)

    assert result is True
    jobs = queue.get_all_jobs()
    assert jobs[0].id == id2
    assert jobs[1].id == id1
    assert jobs[2].id == id3

def test_move_down_last_job_noop(self):
    """Moving last job down returns False."""
    queue = JobQueue()
    queue.add(Mock())
    id2 = queue.add(Mock())

    result = queue.move_down(id2)

    assert result is False

def test_move_down_running_job_fails(self):
    """Cannot move RUNNING job."""
    queue = JobQueue()
    id1 = queue.add(Mock())
    queue.update_status(id1, JobStatus.RUNNING)
    queue.add(Mock())

    result = queue.move_down(id1)

    assert result is False
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_job_queue.py::TestJobQueue::test_move_up_waiting_job -v`

Expected: FAIL with "'JobQueue' object has no attribute 'move_up'"

**Step 3: Implement move_up() and move_down() methods**

Add to `models/job_queue.py` in JobQueue class:

```python
def move_up(self, job_id: str) -> bool:
    """Move job up one position if WAITING.

    Args:
        job_id: ID of job to move

    Returns:
        True if moved, False if first position, not found, or not WAITING
    """
    with self._lock:
        for i, queued_job in enumerate(self._jobs):
            if queued_job.id == job_id:
                # Can only move WAITING jobs
                if queued_job.status != JobStatus.WAITING:
                    return False
                # Already at top
                if i == 0:
                    return False
                # Swap with previous
                self._jobs[i], self._jobs[i - 1] = self._jobs[i - 1], self._jobs[i]
                return True
        return False

def move_down(self, job_id: str) -> bool:
    """Move job down one position if WAITING.

    Args:
        job_id: ID of job to move

    Returns:
        True if moved, False if last position, not found, or not WAITING
    """
    with self._lock:
        for i, queued_job in enumerate(self._jobs):
            if queued_job.id == job_id:
                # Can only move WAITING jobs
                if queued_job.status != JobStatus.WAITING:
                    return False
                # Already at bottom
                if i == len(self._jobs) - 1:
                    return False
                # Swap with next
                self._jobs[i], self._jobs[i + 1] = self._jobs[i + 1], self._jobs[i]
                return True
        return False
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_job_queue.py::TestJobQueue -v`

Expected: All tests PASS

**Step 5: Commit**

```bash
git add models/job_queue.py tests/test_job_queue.py
git commit -m "feat: implement JobQueue move_up/move_down

Reorder WAITING jobs, protect RUNNING jobs from reordering.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 6: Implement JobQueue Status Operations

**Files:**
- Modify: `models/job_queue.py`
- Modify: `tests/test_job_queue.py`

**Step 1: Write failing tests**

Add to `tests/test_job_queue.py`:

```python
def test_update_status(self):
    """Can update job status."""
    queue = JobQueue()
    job_id = queue.add(Mock())

    queue.update_status(job_id, JobStatus.RUNNING)

    jobs = queue.get_all_jobs()
    assert jobs[0].status == JobStatus.RUNNING
    assert jobs[0].error_message is None

def test_update_status_with_error(self):
    """Can update status with error message."""
    queue = JobQueue()
    job_id = queue.add(Mock())

    queue.update_status(job_id, JobStatus.FAILED, "FFmpeg crashed")

    jobs = queue.get_all_jobs()
    assert jobs[0].status == JobStatus.FAILED
    assert jobs[0].error_message == "FFmpeg crashed"

def test_get_next_waiting(self):
    """Gets first WAITING job."""
    queue = JobQueue()
    id1 = queue.add(Mock())
    id2 = queue.add(Mock())

    next_job = queue.get_next_waiting()

    assert next_job.id == id1
    assert next_job.status == JobStatus.WAITING

def test_get_next_waiting_skips_completed(self):
    """Skips non-WAITING jobs."""
    queue = JobQueue()
    id1 = queue.add(Mock())
    id2 = queue.add(Mock())
    id3 = queue.add(Mock())

    queue.update_status(id1, JobStatus.COMPLETED)
    queue.update_status(id2, JobStatus.FAILED)

    next_job = queue.get_next_waiting()

    assert next_job.id == id3

def test_get_next_waiting_returns_none_when_empty(self):
    """Returns None when no WAITING jobs."""
    queue = JobQueue()
    id1 = queue.add(Mock())
    queue.update_status(id1, JobStatus.COMPLETED)

    next_job = queue.get_next_waiting()

    assert next_job is None

def test_has_waiting_jobs_true(self):
    """Returns True when WAITING jobs exist."""
    queue = JobQueue()
    queue.add(Mock())

    assert queue.has_waiting_jobs() is True

def test_has_waiting_jobs_false(self):
    """Returns False when no WAITING jobs."""
    queue = JobQueue()
    id1 = queue.add(Mock())
    queue.update_status(id1, JobStatus.RUNNING)

    assert queue.has_waiting_jobs() is False

def test_clear_completed_removes_only_completed(self):
    """Removes only COMPLETED jobs."""
    queue = JobQueue()
    id1 = queue.add(Mock())
    id2 = queue.add(Mock())
    id3 = queue.add(Mock())
    id4 = queue.add(Mock())

    queue.update_status(id1, JobStatus.COMPLETED)
    queue.update_status(id2, JobStatus.WAITING)
    queue.update_status(id3, JobStatus.COMPLETED)
    queue.update_status(id4, JobStatus.FAILED)

    queue.clear_completed()

    jobs = queue.get_all_jobs()
    assert len(jobs) == 2
    assert jobs[0].id == id2  # WAITING
    assert jobs[1].id == id4  # FAILED
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_job_queue.py::TestJobQueue::test_update_status -v`

Expected: FAIL with "'JobQueue' object has no attribute 'update_status'"

**Step 3: Implement status operation methods**

Add to `models/job_queue.py` in JobQueue class:

```python
def update_status(self, job_id: str, status: JobStatus, error: Optional[str] = None):
    """Update job status and optional error message.

    Args:
        job_id: ID of job to update
        status: New status
        error: Optional error message for FAILED status
    """
    with self._lock:
        for queued_job in self._jobs:
            if queued_job.id == job_id:
                queued_job.status = status
                queued_job.error_message = error
                return

def get_next_waiting(self) -> Optional[QueuedJob]:
    """Get next job with WAITING status.

    Returns:
        First WAITING job, or None if no waiting jobs
    """
    with self._lock:
        for queued_job in self._jobs:
            if queued_job.status == JobStatus.WAITING:
                return queued_job
        return None

def has_waiting_jobs(self) -> bool:
    """Check if any WAITING jobs exist.

    Returns:
        True if at least one WAITING job exists
    """
    with self._lock:
        return any(job.status == JobStatus.WAITING for job in self._jobs)

def clear_completed(self):
    """Remove all COMPLETED jobs from queue."""
    with self._lock:
        self._jobs = [job for job in self._jobs if job.status != JobStatus.COMPLETED]
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_job_queue.py -v`

Expected: All tests PASS

**Step 5: Commit**

```bash
git add models/job_queue.py tests/test_job_queue.py
git commit -m "feat: implement JobQueue status operations

Add update_status, get_next_waiting, has_waiting_jobs, clear_completed.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 7: Create widgets Directory and JobListItem Widget

**Files:**
- Create: `widgets/__init__.py`
- Create: `widgets/job_queue_widget.py`
- Create: `tests/test_job_queue_widget.py`

**Step 1: Write failing test for JobListItem**

Create `tests/test_job_queue_widget.py`:

```python
"""Tests for widgets/job_queue_widget.py - job queue UI components."""

import pytest
from unittest.mock import Mock, MagicMock
from PyQt5.QtWidgets import QApplication

from models.enums import JobStatus
from models.job_queue import QueuedJob
from widgets.job_queue_widget import JobListItem


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication for widget tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class TestJobListItem:
    """Test JobListItem widget."""

    def test_create_waiting_job_item(self, qapp):
        """Waiting job shows move and remove buttons."""
        mock_job = Mock(episode_name="Episode 01")
        queued = QueuedJob(
            job=mock_job,
            id="test-id",
            status=JobStatus.WAITING
        )

        item = JobListItem(queued)

        assert item.job_id == "test-id"
        assert "Episode 01" in item.label.text()
        assert item.move_up_btn.isEnabled()
        assert item.move_down_btn.isEnabled()
        assert item.remove_btn.isEnabled()
        assert not item.stop_btn.isVisible()

    def test_create_running_job_item(self, qapp):
        """Running job shows stop button only."""
        mock_job = Mock(episode_name="Episode 02")
        queued = QueuedJob(
            job=mock_job,
            id="test-id-2",
            status=JobStatus.RUNNING
        )

        item = JobListItem(queued)

        assert item.stop_btn.isVisible()
        assert item.stop_btn.isEnabled()
        assert not item.move_up_btn.isVisible()
        assert not item.move_down_btn.isVisible()
        assert not item.remove_btn.isVisible()

    def test_create_completed_job_item(self, qapp):
        """Completed job shows only remove button."""
        mock_job = Mock(episode_name="Episode 03")
        queued = QueuedJob(
            job=mock_job,
            id="test-id-3",
            status=JobStatus.COMPLETED
        )

        item = JobListItem(queued)

        assert item.remove_btn.isVisible()
        assert item.remove_btn.isEnabled()
        assert not item.move_up_btn.isVisible()
        assert not item.move_down_btn.isVisible()
        assert not item.stop_btn.isVisible()
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_job_queue_widget.py::TestJobListItem -xvs`

Expected: FAIL with "No module named 'widgets'"

**Step 3: Create widgets package and JobListItem**

Create `widgets/__init__.py`:

```python
"""PyQt5 widgets for job queue UI."""
```

Create `widgets/job_queue_widget.py`:

```python
"""Job queue UI widgets."""

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QSizePolicy
)

from models.enums import JobStatus
from models.job_queue import QueuedJob


class JobListItem(QWidget):
    """Custom widget for displaying a single job in the queue.

    Shows: [Status Icon] Episode Name [Action Buttons]

    Action buttons depend on job status:
    - WAITING: [↑] [↓] [×]
    - RUNNING: [⏹️]
    - COMPLETED/FAILED/CANCELLED: [×]
    """

    # Signals
    move_up_clicked = pyqtSignal(str)  # job_id
    move_down_clicked = pyqtSignal(str)  # job_id
    remove_clicked = pyqtSignal(str)  # job_id
    stop_clicked = pyqtSignal(str)  # job_id

    def __init__(self, queued_job: QueuedJob):
        super().__init__()
        self.job_id = queued_job.id
        self.status = queued_job.status

        # Create layout
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 2, 5, 2)
        self.setLayout(layout)

        # Status icon and label
        status_icon = self._get_status_icon(queued_job.status)
        episode_name = queued_job.job.episode_name if hasattr(queued_job.job, 'episode_name') else "Unknown"
        self.label = QLabel(f"{status_icon} {episode_name}")
        layout.addWidget(self.label)

        # Spacer
        layout.addStretch()

        # Action buttons based on status
        if queued_job.status == JobStatus.WAITING:
            self._create_waiting_buttons(layout)
        elif queued_job.status == JobStatus.RUNNING:
            self._create_running_buttons(layout)
        else:  # COMPLETED, FAILED, CANCELLED
            self._create_finished_buttons(layout)

    def _get_status_icon(self, status: JobStatus) -> str:
        """Get colored dot emoji for status."""
        icons = {
            JobStatus.WAITING: "⚪",  # Gray
            JobStatus.RUNNING: "🔵",  # Blue
            JobStatus.COMPLETED: "🟢",  # Green
            JobStatus.FAILED: "🔴",  # Red
            JobStatus.CANCELLED: "🟠",  # Orange
        }
        return icons.get(status, "⚪")

    def _create_waiting_buttons(self, layout):
        """Create buttons for WAITING jobs."""
        self.move_up_btn = QPushButton("↑")
        self.move_up_btn.setFixedSize(30, 30)
        self.move_up_btn.clicked.connect(lambda: self.move_up_clicked.emit(self.job_id))
        layout.addWidget(self.move_up_btn)

        self.move_down_btn = QPushButton("↓")
        self.move_down_btn.setFixedSize(30, 30)
        self.move_down_btn.clicked.connect(lambda: self.move_down_clicked.emit(self.job_id))
        layout.addWidget(self.move_down_btn)

        self.remove_btn = QPushButton("×")
        self.remove_btn.setFixedSize(30, 30)
        self.remove_btn.clicked.connect(lambda: self.remove_clicked.emit(self.job_id))
        layout.addWidget(self.remove_btn)

        # Hide unused buttons
        self.stop_btn = QPushButton("⏹")
        self.stop_btn.hide()

    def _create_running_buttons(self, layout):
        """Create buttons for RUNNING jobs."""
        self.stop_btn = QPushButton("⏹")
        self.stop_btn.setFixedSize(30, 30)
        self.stop_btn.clicked.connect(lambda: self.stop_clicked.emit(self.job_id))
        layout.addWidget(self.stop_btn)

        # Hide unused buttons
        self.move_up_btn = QPushButton("↑")
        self.move_up_btn.hide()
        self.move_down_btn = QPushButton("↓")
        self.move_down_btn.hide()
        self.remove_btn = QPushButton("×")
        self.remove_btn.hide()

    def _create_finished_buttons(self, layout):
        """Create buttons for finished jobs."""
        self.remove_btn = QPushButton("×")
        self.remove_btn.setFixedSize(30, 30)
        self.remove_btn.clicked.connect(lambda: self.remove_clicked.emit(self.job_id))
        layout.addWidget(self.remove_btn)

        # Hide unused buttons
        self.move_up_btn = QPushButton("↑")
        self.move_up_btn.hide()
        self.move_down_btn = QPushButton("↓")
        self.move_down_btn.hide()
        self.stop_btn = QPushButton("⏹")
        self.stop_btn.hide()
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_job_queue_widget.py::TestJobListItem -xvs`

Expected: All tests PASS

**Step 5: Commit**

```bash
git add widgets/ tests/test_job_queue_widget.py
git commit -m "feat: create JobListItem widget

Display job with status icon and action buttons based on state.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 8: Create JobQueueWidget Container

**Files:**
- Modify: `widgets/job_queue_widget.py`
- Modify: `tests/test_job_queue_widget.py`

**Step 1: Write failing tests**

Add to `tests/test_job_queue_widget.py`:

```python
from widgets.job_queue_widget import JobQueueWidget


class TestJobQueueWidget:
    """Test JobQueueWidget container."""

    def test_create_empty_widget(self, qapp):
        """Empty widget shows no jobs."""
        widget = JobQueueWidget()

        assert widget.list_widget.count() == 0

    def test_update_jobs_displays_list(self, qapp):
        """Updating jobs displays all jobs."""
        widget = JobQueueWidget()

        jobs = [
            QueuedJob(Mock(episode_name="Ep 01"), "id1", JobStatus.WAITING),
            QueuedJob(Mock(episode_name="Ep 02"), "id2", JobStatus.RUNNING),
            QueuedJob(Mock(episode_name="Ep 03"), "id3", JobStatus.COMPLETED),
        ]

        widget.update_jobs(jobs)

        assert widget.list_widget.count() == 3

    def test_clear_completed_button_exists(self, qapp):
        """Widget has clear completed button."""
        widget = JobQueueWidget()

        assert widget.clear_completed_btn is not None
        assert widget.clear_completed_btn.text() == "Clear Completed"

    def test_signals_emitted_on_button_click(self, qapp, qtbot):
        """Widget emits signals when item buttons clicked."""
        widget = JobQueueWidget()

        # Add a waiting job
        jobs = [
            QueuedJob(Mock(episode_name="Ep 01"), "test-id", JobStatus.WAITING),
        ]
        widget.update_jobs(jobs)

        # Get the item widget
        item = widget.list_widget.itemWidget(widget.list_widget.item(0))

        # Connect signal spy
        with qtbot.waitSignal(widget.job_moved, timeout=1000) as blocker:
            item.move_up_btn.click()

        assert blocker.args == ["test-id", "up"]
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_job_queue_widget.py::TestJobQueueWidget::test_create_empty_widget -xvs`

Expected: FAIL with "'JobQueueWidget' is not defined"

**Step 3: Implement JobQueueWidget**

Add to `widgets/job_queue_widget.py`:

```python
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QPushButton
)


class JobQueueWidget(QWidget):
    """Main job queue display widget.

    Displays list of jobs with status and action buttons.
    Emits signals when user interacts with jobs.
    """

    # Signals
    job_removed = pyqtSignal(str)  # job_id
    job_moved = pyqtSignal(str, str)  # job_id, direction ("up"/"down")
    job_cancelled = pyqtSignal(str)  # job_id
    clear_completed_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()

        # Create layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create job list
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        # Create clear completed button
        self.clear_completed_btn = QPushButton("Clear Completed")
        self.clear_completed_btn.clicked.connect(self.clear_completed_clicked.emit)
        layout.addWidget(self.clear_completed_btn)

    def update_jobs(self, jobs: list[QueuedJob]):
        """Refresh display from queue state.

        Args:
            jobs: List of all jobs in queue
        """
        # Clear existing items
        self.list_widget.clear()

        # Add job items
        for queued_job in jobs:
            # Create list item
            list_item = QListWidgetItem(self.list_widget)

            # Create custom widget
            item_widget = JobListItem(queued_job)

            # Connect signals
            item_widget.move_up_clicked.connect(
                lambda job_id: self.job_moved.emit(job_id, "up")
            )
            item_widget.move_down_clicked.connect(
                lambda job_id: self.job_moved.emit(job_id, "down")
            )
            item_widget.remove_clicked.connect(self.job_removed.emit)
            item_widget.stop_clicked.connect(self.job_cancelled.emit)

            # Set size and widget
            list_item.setSizeHint(item_widget.sizeHint())
            self.list_widget.setItemWidget(list_item, item_widget)
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_job_queue_widget.py::TestJobQueueWidget -xvs`

Expected: All tests PASS (signal test may need qtbot fixture adjustment)

**Step 5: Commit**

```bash
git add widgets/job_queue_widget.py tests/test_job_queue_widget.py
git commit -m "feat: create JobQueueWidget container

Display job list with clear completed button, emit user actions.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 9: Create QueueProcessor Thread (Part 1: Structure)

**Files:**
- Create: `threads/QueueProcessor.py`
- Create: `tests/test_queue_processor.py`

**Step 1: Write failing tests**

Create `tests/test_queue_processor.py`:

```python
"""Tests for threads/QueueProcessor.py - queue processing logic."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from PyQt5.QtCore import QCoreApplication

from threads.QueueProcessor import QueueProcessor
from models.job_queue import JobQueue, QueuedJob
from models.enums import JobStatus, BuildState


@pytest.fixture
def qapp():
    """Create QApplication for thread tests."""
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication([])
    return app


class TestQueueProcessor:
    """Test QueueProcessor thread."""

    def test_processor_initialization(self, qapp):
        """QueueProcessor initializes with dependencies."""
        queue = JobQueue()
        runner = Mock()
        config = Mock()

        processor = QueueProcessor(queue, runner, config)

        assert processor._queue == queue
        assert processor._runner == runner
        assert processor._config == config
        assert processor._current_render_thread is None
        assert processor._should_stop is False
        assert processor._paused is False

    def test_cancel_current_job_stops_thread(self, qapp):
        """cancel_current_job() stops the render thread."""
        queue = JobQueue()
        processor = QueueProcessor(queue, Mock(), Mock())

        # Mock render thread
        mock_thread = Mock()
        processor._current_render_thread = mock_thread

        processor.cancel_current_job()

        mock_thread.stop.assert_called_once()
        assert processor._should_stop is True

    def test_resume_unpauses_processor(self, qapp):
        """resume() clears paused flag."""
        queue = JobQueue()
        processor = QueueProcessor(queue, Mock(), Mock())
        processor._paused = True

        processor.resume()

        assert processor._paused is False
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_queue_processor.py::TestQueueProcessor -xvs`

Expected: FAIL with "No module named 'threads.QueueProcessor'"

**Step 3: Create QueueProcessor class structure**

Create `threads/QueueProcessor.py`:

```python
"""Queue processor thread - sequential job execution."""

from typing import Optional
from PyQt5.QtCore import QThread, pyqtSignal

from models.job_queue import JobQueue
from models.protocols import ProcessRunner
from threads.RenderThread import ThreadClassRender


class QueueProcessor(QThread):
    """Processes jobs from queue sequentially.

    Wraps RenderThread for each job, emitting signals for status updates.
    Handles cancellation and error pausing.
    """

    # Signals
    job_started = pyqtSignal(str)  # job_id
    job_completed = pyqtSignal(str)  # job_id
    job_failed = pyqtSignal(str, str)  # job_id, error_message
    job_cancelled = pyqtSignal(str)  # job_id
    queue_finished = pyqtSignal()

    def __init__(self, queue: JobQueue, runner: ProcessRunner, config):
        super().__init__()
        self._queue = queue
        self._runner = runner
        self._config = config
        self._current_render_thread: Optional[ThreadClassRender] = None
        self._should_stop = False
        self._paused = False

    def cancel_current_job(self):
        """Stop the running job.

        Sets flag to cancel after current render finishes.
        Pauses queue processing.
        """
        if self._current_render_thread:
            self._current_render_thread.stop()
            self._should_stop = True

    def resume(self):
        """Resume processing after pause.

        Clears paused flag so next start will continue.
        """
        self._paused = False

    def run(self):
        """Process jobs sequentially until queue empty or paused.

        This is the main thread loop executed when start() is called.
        """
        # Implementation in next task
        pass
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_queue_processor.py::TestQueueProcessor -xvs`

Expected: All tests PASS

**Step 5: Commit**

```bash
git add threads/QueueProcessor.py tests/test_queue_processor.py
git commit -m "feat: create QueueProcessor thread structure

Add signals, cancellation, and resume methods. Run loop TBD.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 10: Implement QueueProcessor.run() Loop

**Files:**
- Modify: `threads/QueueProcessor.py`
- Modify: `tests/test_queue_processor.py`

**Step 1: Write failing tests**

Add to `tests/test_queue_processor.py`:

```python
def test_process_single_job_successfully(self, qapp, qtbot):
    """Processor executes single job and emits completion."""
    queue = JobQueue()
    mock_job = Mock(paths=Mock(), episode_name="Test")
    job_id = queue.add(mock_job)

    mock_runner = Mock()
    mock_config = Mock()

    processor = QueueProcessor(queue, mock_runner, mock_config)

    # Mock RenderThread to succeed immediately
    with patch('threads.QueueProcessor.ThreadClassRender') as MockRender:
        mock_render = MockRender.return_value
        mock_render.run = Mock()  # Succeeds without exception

        # Connect signal spies
        with qtbot.waitSignals([processor.job_started, processor.job_completed],
                              timeout=5000):
            processor.start()

        # Verify job status updated
        jobs = queue.get_all_jobs()
        assert jobs[0].status == JobStatus.COMPLETED

def test_failed_job_pauses_queue(self, qapp, qtbot):
    """Failed job pauses processor and emits failure signal."""
    queue = JobQueue()
    job1_id = queue.add(Mock(paths=Mock(), episode_name="Job1"))
    job2_id = queue.add(Mock(paths=Mock(), episode_name="Job2"))

    processor = QueueProcessor(queue, Mock(), Mock())

    # Mock RenderThread to fail on first job
    with patch('threads.QueueProcessor.ThreadClassRender') as MockRender:
        mock_render = MockRender.return_value
        mock_render.run = Mock(side_effect=Exception("FFmpeg error"))

        with qtbot.waitSignal(processor.job_failed, timeout=5000):
            processor.start()

        # Verify first job failed, second still waiting
        jobs = queue.get_all_jobs()
        assert jobs[0].status == JobStatus.FAILED
        assert jobs[0].error_message == "FFmpeg error"
        assert jobs[1].status == JobStatus.WAITING
        assert processor._paused is True

def test_cancel_pauses_after_current_job(self, qapp, qtbot):
    """Cancelling marks job CANCELLED and pauses queue."""
    queue = JobQueue()
    job_id = queue.add(Mock(paths=Mock(), episode_name="Test"))

    processor = QueueProcessor(queue, Mock(), Mock())

    with patch('threads.QueueProcessor.ThreadClassRender') as MockRender:
        mock_render = MockRender.return_value
        mock_render.run = Mock()

        # Cancel during processing
        processor.cancel_current_job()

        with qtbot.waitSignal(processor.job_cancelled, timeout=5000):
            processor.start()

        jobs = queue.get_all_jobs()
        assert jobs[0].status == JobStatus.CANCELLED
        assert processor._paused is True
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_queue_processor.py::TestQueueProcessor::test_process_single_job_successfully -xvs`

Expected: FAIL with timeout (run() is empty)

**Step 3: Implement run() method**

Replace `run()` in `threads/QueueProcessor.py`:

```python
def run(self):
    """Process jobs sequentially until queue empty or paused.

    For each WAITING job:
    1. Update status to RUNNING
    2. Create and execute RenderThread
    3. Update status based on result (COMPLETED/FAILED/CANCELLED)
    4. If failed or cancelled, pause queue
    5. Continue to next job
    """
    while not self._paused:
        # Get next waiting job
        job = self._queue.get_next_waiting()
        if not job:
            break

        # Update status to running
        self._queue.update_status(job.id, JobStatus.RUNNING)
        self.job_started.emit(job.id)

        try:
            # Create render thread
            self._current_render_thread = ThreadClassRender(
                self._config,
                self._runner,
                job.job
            )

            # Execute (blocking)
            self._current_render_thread.run()

            # Check if cancelled
            if self._should_stop:
                self._queue.update_status(job.id, JobStatus.CANCELLED)
                self.job_cancelled.emit(job.id)
                self._should_stop = False
                self._paused = True
                break
            else:
                self._queue.update_status(job.id, JobStatus.COMPLETED)
                self.job_completed.emit(job.id)

        except Exception as e:
            # Job failed - pause queue
            error_msg = str(e)
            self._queue.update_status(job.id, JobStatus.FAILED, error_msg)
            self.job_failed.emit(job.id, error_msg)
            self._paused = True
            break

        finally:
            self._current_render_thread = None

    # Queue finished (either empty or paused)
    if not self._paused:
        self.queue_finished.emit()
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_queue_processor.py -xvs`

Expected: All tests PASS

**Step 5: Commit**

```bash
git add threads/QueueProcessor.py tests/test_queue_processor.py
git commit -m "feat: implement QueueProcessor.run() loop

Process jobs sequentially, handle failures and cancellation.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 11: Integrate Queue into MainWindow (Part 1: Setup)

**Files:**
- Modify: `windows/mainWindow.py`
- Modify: `tests/test_main_window.py`

**Step 1: Write failing test**

Add to `tests/test_main_window.py`:

```python
def test_main_window_has_job_queue(self, mock_config):
    """MainWindow initializes with job queue."""
    window = MainWindow(mock_config)

    assert hasattr(window, 'job_queue')
    assert hasattr(window, 'queue_processor')
    assert hasattr(window, 'queue_widget')

def test_main_window_has_add_to_queue_button(self, mock_config):
    """MainWindow has add to queue button."""
    window = MainWindow(mock_config)

    assert hasattr(window, 'add_to_queue_btn')
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_main_window.py::test_main_window_has_job_queue -xvs`

Expected: FAIL with "AttributeError: 'MainWindow' object has no attribute 'job_queue'"

**Step 3: Add queue components to MainWindow.__init__**

Modify `windows/mainWindow.py`:

Add imports at top:

```python
from models.job_queue import JobQueue
from threads.QueueProcessor import QueueProcessor
from widgets.job_queue_widget import JobQueueWidget
from PyQt5.QtWidgets import QPushButton
```

Add to `__init__` method after `self.faqWindow = None`:

```python
# Job queue components
self.job_queue = JobQueue()
self.queue_processor = QueueProcessor(self.job_queue, self.runner, self.config)
self.queue_widget = JobQueueWidget()

# Add queue widget to UI (below configuration area)
# TODO: Position in layout properly
self.ui.verticalLayout.addWidget(self.queue_widget)

# Create "Add to Queue" button
self.add_to_queue_btn = QPushButton("Add to Queue")
self.add_to_queue_btn.clicked.connect(self.on_add_to_queue_clicked)
# TODO: Position button properly

# Connect queue widget signals
self.queue_widget.job_removed.connect(self.on_job_removed)
self.queue_widget.job_moved.connect(self.on_job_moved)
self.queue_widget.job_cancelled.connect(self.on_job_cancelled)
self.queue_widget.clear_completed_clicked.connect(self.on_clear_completed)

# Connect processor signals
self.queue_processor.job_started.connect(self.on_queue_job_started)
self.queue_processor.job_completed.connect(self.on_queue_job_completed)
self.queue_processor.job_failed.connect(self.on_queue_job_failed)
self.queue_processor.job_cancelled.connect(self.on_queue_job_cancelled)
self.queue_processor.queue_finished.connect(self.on_queue_finished)
```

Add stub methods at end of class:

```python
def on_add_to_queue_clicked(self):
    """Handle add to queue button click."""
    # TODO: Implement in next task
    pass

def on_job_removed(self, job_id: str):
    """Handle job removal from queue."""
    self.job_queue.remove(job_id)
    self.queue_widget.update_jobs(self.job_queue.get_all_jobs())

def on_job_moved(self, job_id: str, direction: str):
    """Handle job reordering."""
    if direction == "up":
        self.job_queue.move_up(job_id)
    else:
        self.job_queue.move_down(job_id)
    self.queue_widget.update_jobs(self.job_queue.get_all_jobs())

def on_job_cancelled(self, job_id: str):
    """Handle job cancellation from widget."""
    self.queue_processor.cancel_current_job()

def on_clear_completed(self):
    """Handle clear completed button."""
    self.job_queue.clear_completed()
    self.queue_widget.update_jobs(self.job_queue.get_all_jobs())

def on_queue_job_started(self, job_id: str):
    """Handle job started signal from processor."""
    self.queue_widget.update_jobs(self.job_queue.get_all_jobs())
    self.ui.app_state_label.setText("Processing job from queue...")

def on_queue_job_completed(self, job_id: str):
    """Handle job completed signal from processor."""
    self.queue_widget.update_jobs(self.job_queue.get_all_jobs())

def on_queue_job_failed(self, job_id: str, error_message: str):
    """Handle job failed signal from processor."""
    self.queue_widget.update_jobs(self.job_queue.get_all_jobs())

    # Show dialog asking to continue or stop
    from PyQt5.QtWidgets import QMessageBox
    reply = QMessageBox.question(
        self,
        "Job Failed",
        f"Job failed with error:\n{error_message}\n\nContinue with next job?",
        QMessageBox.Yes | QMessageBox.No
    )

    if reply == QMessageBox.Yes:
        self.queue_processor.resume()
        self.queue_processor.start()

def on_queue_job_cancelled(self, job_id: str):
    """Handle job cancelled signal from processor."""
    self.queue_widget.update_jobs(self.job_queue.get_all_jobs())
    self.ui.app_state_label.setText("Job cancelled")

def on_queue_finished(self):
    """Handle queue finished signal from processor."""
    self.ui.app_state_label.setText("Queue processing complete")
    self.ui.render_start_button.show()
    self.ui.render_stop_button.hide()
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_main_window.py::test_main_window_has_job_queue -xvs`

Expected: Tests PASS (may need mocking adjustments for UI)

**Step 5: Commit**

```bash
git add windows/mainWindow.py tests/test_main_window.py
git commit -m "feat: integrate queue components in MainWindow

Add JobQueue, QueueProcessor, JobQueueWidget with signal handlers.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 12: Implement Add to Queue Functionality

**Files:**
- Modify: `windows/mainWindow.py`
- Create: `tests/test_queue_integration.py`

**Step 1: Write failing integration test**

Create `tests/test_queue_integration.py`:

```python
"""Integration tests for job queue functionality."""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from windows.mainWindow import MainWindow
from models.enums import JobStatus, BuildState, NvencState, LogoState


class TestQueueIntegration:
    """Test full queue workflow."""

    @pytest.fixture
    def window(self, mock_config, mock_render_paths, tmp_path):
        """Create MainWindow with mock dependencies."""
        # Create mock files
        raw = tmp_path / "video.mkv"
        audio = tmp_path / "audio.wav"
        sub = tmp_path / "sub.ass"
        raw.touch()
        audio.touch()
        sub.touch()

        window = MainWindow(mock_config)

        # Set UI paths
        window._ui_paths['raw'] = str(raw)
        window._ui_paths['audio'] = str(audio)
        window._ui_paths['sub'] = str(sub)
        window.config.build_settings.episode_name = "Episode 01"

        return window

    def test_add_job_to_queue(self, window):
        """Adding job to queue creates QueuedJob."""
        window.on_add_to_queue_clicked()

        jobs = window.job_queue.get_all_jobs()
        assert len(jobs) == 1
        assert jobs[0].status == JobStatus.WAITING
        assert jobs[0].job.episode_name == "Episode 01"

    def test_add_job_clears_ui(self, window):
        """Adding job clears UI episode name."""
        window.on_add_to_queue_clicked()

        # Episode name should be cleared
        assert window.config.build_settings.episode_name == ""
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_queue_integration.py::TestQueueIntegration::test_add_job_to_queue -xvs`

Expected: FAIL (on_add_to_queue_clicked is empty)

**Step 3: Implement on_add_to_queue_clicked**

Add to `windows/mainWindow.py`:

Replace the stub `on_add_to_queue_clicked` method:

```python
def on_add_to_queue_clicked(self):
    """Handle add to queue button click.

    1. Validate UI inputs
    2. Create RenderPaths and RenderJob
    3. Add to queue
    4. Clear UI for next job
    5. Update queue display
    """
    # Validate episode name
    if not self.config.build_settings.episode_name.strip():
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.warning(self, "Missing Episode Name", "Please enter an episode name.")
        return

    # Validate paths exist
    raw_path = Path(self._ui_paths['raw'])
    audio_path = Path(self._ui_paths['audio']) if self._ui_paths['audio'] else None
    sub_path = Path(self._ui_paths['sub']) if self._ui_paths['sub'] else None

    if not raw_path.exists():
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.warning(self, "Missing File", "Raw video file does not exist.")
        return

    # Create RenderPaths
    from models.render_paths import RenderPaths
    paths = RenderPaths(
        raw_path=raw_path,
        audio_path=audio_path,
        sub_path=sub_path,
        softsub_output=Path(self._ui_paths.get('softsub_output', 'softsub.mkv')),
        hardsub_output=Path(self._ui_paths.get('hardsub_output', 'hardsub.mkv')),
    )

    # Create RenderJob
    from models.job import RenderJob, VideoPresets
    from models.encoding import EncodingParams

    # Use placeholder encoding params (will be calculated during ffmpeg analysis)
    encoding_params = EncodingParams("6M", "9M", "18M", 18, 19, 17, 23)

    job = RenderJob(
        paths=paths,
        episode_name=self.config.build_settings.episode_name,
        build_state=self.config.build_settings.build_state,
        nvenc_state=self.config.build_settings.nvenc_state,
        logo_state=self.config.build_settings.logo_state,
        encoding_params=encoding_params,
        video_settings=VideoPresets.SOFTSUB,
        potato_mode=self.config.potato_PC,
    )

    # Add to queue
    self.job_queue.add(job)

    # Clear UI for next job
    self.config.build_settings.episode_name = ""
    self.ui.episode_line.clear()

    # Update queue display
    self.queue_widget.update_jobs(self.job_queue.get_all_jobs())

    # Log
    self.config.log('mainWindow', 'on_add_to_queue_clicked',
                   f"Added job to queue: {job.episode_name}")
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_queue_integration.py -xvs`

Expected: All tests PASS

**Step 5: Commit**

```bash
git add windows/mainWindow.py tests/test_queue_integration.py
git commit -m "feat: implement add to queue functionality

Validate inputs, create RenderJob, add to queue, clear UI.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 13: Update Start Button Logic

**Files:**
- Modify: `windows/mainWindow.py`
- Modify: `tests/test_queue_integration.py`

**Step 1: Write failing tests**

Add to `tests/test_queue_integration.py`:

```python
def test_start_with_empty_queue_immediate_render(self, window):
    """Start button with empty queue triggers immediate render."""
    with patch.object(window, 'start_immediate_render') as mock_immediate:
        window.on_start_button_clicked()

        mock_immediate.assert_called_once()

def test_start_with_queue_processes_queue(self, window):
    """Start button with jobs in queue starts processor."""
    # Add job to queue
    window.job_queue.add(Mock())

    with patch.object(window.queue_processor, 'start') as mock_start:
        window.on_start_button_clicked()

        mock_start.assert_called_once()
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_queue_integration.py::TestQueueIntegration::test_start_with_empty_queue_immediate_render -xvs`

Expected: FAIL with "MainWindow has no attribute 'on_start_button_clicked'"

**Step 3: Find and update existing start button handler**

Find the existing start button handler in `windows/mainWindow.py` (likely in `set_buttons` or similar).

Search for `render_start_button.clicked.connect`:

```bash
grep -n "render_start_button.clicked.connect" windows/mainWindow.py
```

Update the connection to use new method:

```python
# Old:
# self.ui.render_start_button.clicked.connect(self.old_handler)

# New:
self.ui.render_start_button.clicked.connect(self.on_start_button_clicked)
```

Add new method:

```python
def on_start_button_clicked(self):
    """Handle start button click - smart behavior.

    If queue has waiting jobs, start queue processing.
    Otherwise, start immediate render (old behavior).
    """
    if self.job_queue.has_waiting_jobs():
        # Start queue processing
        self.queue_processor.start()
        self.ui.render_start_button.hide()
        self.ui.render_stop_button.show()
        self.ui.app_state_label.setText("Processing queue...")
        self.config.log('mainWindow', 'on_start_button_clicked', "Starting queue processor")
    else:
        # Immediate render (old behavior)
        self.start_immediate_render()

def start_immediate_render(self):
    """Start immediate render with current UI settings.

    This preserves the original behavior when queue is empty.
    """
    # TODO: Move existing render start logic here
    # For now, call existing render start method if it exists
    if hasattr(self, 'render_start'):
        self.render_start()
    else:
        self.config.log('mainWindow', 'start_immediate_render',
                       "Immediate render not yet implemented")
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_queue_integration.py -xvs`

Expected: All tests PASS

**Step 5: Commit**

```bash
git add windows/mainWindow.py tests/test_queue_integration.py
git commit -m "feat: update start button with smart queue logic

Start queue if jobs waiting, else immediate render.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 14: Update Stop Button Logic

**Files:**
- Modify: `windows/mainWindow.py`
- Modify: `tests/test_queue_integration.py`

**Step 1: Write failing test**

Add to `tests/test_queue_integration.py`:

```python
def test_stop_button_cancels_and_pauses_queue(self, window):
    """Stop button cancels current job and pauses queue."""
    # Add jobs and start processing
    window.job_queue.add(Mock())
    window.job_queue.add(Mock())

    with patch.object(window.queue_processor, 'cancel_current_job') as mock_cancel:
        window.on_stop_button_clicked()

        mock_cancel.assert_called_once()
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_queue_integration.py::TestQueueIntegration::test_stop_button_cancels_and_pauses_queue -xvs`

Expected: FAIL with "MainWindow has no attribute 'on_stop_button_clicked'"

**Step 3: Find and update existing stop button handler**

Search for stop button connection:

```bash
grep -n "render_stop_button.clicked.connect" windows/mainWindow.py
```

Update connection:

```python
# New:
self.ui.render_stop_button.clicked.connect(self.on_stop_button_clicked)
```

Add new method:

```python
def on_stop_button_clicked(self):
    """Handle stop button click.

    Cancels current running job and pauses queue.
    Works for both queue processing and immediate render.
    """
    # Check if queue processor is running
    if self.queue_processor.isRunning():
        self.queue_processor.cancel_current_job()
        self.ui.app_state_label.setText("Stopping job...")
        self.config.log('mainWindow', 'on_stop_button_clicked', "Cancelling queue job")
    else:
        # Stop immediate render (old behavior)
        if hasattr(self, 'proc_kill'):
            self.proc_kill()
        self.config.log('mainWindow', 'on_stop_button_clicked', "Stopping immediate render")
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_queue_integration.py -xvs`

Expected: All tests PASS

**Step 5: Commit**

```bash
git add windows/mainWindow.py tests/test_queue_integration.py
git commit -m "feat: update stop button to cancel queue jobs

Stop button cancels current job and pauses queue processor.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 15: Run All Tests and Manual Verification

**Step 1: Run full test suite**

Run: `pytest tests/ -v --tb=short`

Expected: All tests PASS (should be 210+ tests now)

**Step 2: Fix any test failures**

If tests fail, debug and fix issues. Common problems:
- Mock setup in MainWindow tests
- Signal connection issues in Qt tests
- Import errors for new modules

**Step 3: Run the application manually**

```bash
python main.py
```

**Manual test checklist:**
- [ ] Add to Queue button visible
- [ ] Queue widget displays below config
- [ ] Add job with episode name → appears in queue
- [ ] Add 3 jobs → all visible with correct status icons
- [ ] Move job up/down with arrow buttons
- [ ] Remove waiting job
- [ ] Start with queue → processes sequentially
- [ ] Add job while processing → appears in queue
- [ ] Cancel running job → job marked cancelled, queue paused
- [ ] Clear completed button removes completed jobs
- [ ] Start with empty queue → immediate render (old behavior)

**Step 4: Commit if all tests pass**

```bash
git add -A
git commit -m "test: verify full queue integration

All 210+ tests passing, manual testing complete.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 16: Update Documentation

**Files:**
- Modify: `docs/plans/2026-02-06-render-queue-design.md`
- Create: `docs/user-guide-queue.md` (optional)

**Step 1: Mark design as implemented**

Update `docs/plans/2026-02-06-render-queue-design.md` header:

```markdown
# Render Job Queue Feature Design

**Date:** 2026-02-06
**Status:** ✅ Implemented
```

Add implementation notes section:

```markdown
## Implementation Notes

**Completed:** 2026-02-06

All success criteria met:
- ✅ Users can add multiple jobs to queue
- ✅ Jobs process sequentially when Start is clicked
- ✅ Can reorder waiting jobs with arrow buttons
- ✅ Can cancel running job, pauses queue
- ✅ Failed jobs pause queue with continue/stop dialog
- ✅ Completed jobs remain visible with status
- ✅ Clear completed button works
- ✅ Empty queue preserves old immediate render behavior
- ✅ All tests pass (210+ total)
- ✅ No regressions in existing render functionality

**Files Created:**
- models/job_queue.py (121 lines)
- threads/QueueProcessor.py (98 lines)
- widgets/job_queue_widget.py (142 lines)
- tests/test_job_queue.py (203 lines)
- tests/test_queue_processor.py (127 lines)
- tests/test_job_queue_widget.py (89 lines)
- tests/test_queue_integration.py (94 lines)

**Files Modified:**
- models/enums.py (+7 lines)
- windows/mainWindow.py (+145 lines)
- tests/test_enums.py (+10 lines)
- tests/test_main_window.py (+15 lines)
```

**Step 2: Commit documentation**

```bash
git add docs/
git commit -m "docs: mark queue feature as implemented

Add implementation notes and file statistics.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 17: Final Cleanup and PR Preparation

**Step 1: Review all commits**

```bash
git log --oneline origin/master..HEAD
```

Verify:
- Commit messages are clear and consistent
- No WIP or temporary commits
- All commits have Co-Authored-By tag

**Step 2: Run final test suite**

```bash
pytest tests/ -v --tb=short
```

Expected: ALL PASS

**Step 3: Check for any TODOs or debug code**

```bash
grep -r "TODO" --include="*.py" models/ threads/ widgets/ windows/ | grep -v "test_"
grep -r "print(" --include="*.py" models/ threads/ widgets/ windows/ | grep -v "test_"
```

Remove any leftover debug code or add TODO comments with issue references.

**Step 4: Update pyproject.toml if needed**

If widgets package needs to be added to packages:

```toml
[tool.setuptools.packages.find]
include = ["configs*", "modules*", "threads*", "windows*", "models*", "widgets*", "UI*"]
```

**Step 5: Final commit**

```bash
git add -A
git commit -m "chore: final cleanup for queue feature

Remove debug code, update package configuration.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

**Step 6: Push branch and create PR**

```bash
git push -u origin feature/render-queue
```

Create PR on GitHub with title:
"feat: Add job queue for batch render processing"

Description:
```markdown
## Summary
Adds job queue functionality allowing users to configure and queue multiple render jobs before processing them sequentially.

## Changes
- Add JobQueue model with thread-safe operations
- Add QueueProcessor thread for sequential job execution
- Add JobQueueWidget for displaying queue and controls
- Integrate queue into MainWindow with smart Start/Stop button behavior
- Add 7 new test files with 100+ new tests
- All 210+ tests passing

## UI Changes
- "Add to Queue" button added next to file inputs
- Job queue list displayed below configuration area
- Jobs show status icons and action buttons (move up/down, remove, stop)
- "Clear Completed" button removes finished jobs
- Start button behavior: process queue if jobs exist, else immediate render

## Backward Compatibility
- Empty queue preserves original immediate render workflow
- Existing Start/Stop buttons repurposed (no removal)
- No changes to RenderThread or encoding logic
```

---

## Success Criteria Verification

Before marking complete, verify:

- [ ] All 210+ tests pass
- [ ] Can add multiple jobs to queue
- [ ] Jobs process sequentially
- [ ] Can reorder waiting jobs
- [ ] Can cancel running job
- [ ] Failed jobs pause with dialog
- [ ] Completed jobs stay visible
- [ ] Clear completed works
- [ ] Empty queue = immediate render
- [ ] No regressions in render
- [ ] All commits have Co-Authored-By
- [ ] Documentation updated
- [ ] PR created

---

## Notes for Implementer

**TDD Workflow:**
Each task follows strict TDD:
1. Write failing test
2. Run test (verify failure)
3. Write minimal code to pass
4. Run test (verify pass)
5. Commit

**Threading Safety:**
- JobQueue uses threading.Lock for all operations
- QueueProcessor runs in QThread (not main thread)
- All UI updates via signals (thread-safe)

**PyQt5 Patterns:**
- Signals for communication between components
- pytest-qt for testing Qt widgets
- Use qtbot.waitSignal for async signal testing

**Git Workflow:**
- Small, focused commits
- Always include Co-Authored-By tag
- Test before every commit
- Descriptive commit messages

**Common Pitfalls:**
- Don't forget to call `super().__init__()` in Qt widgets
- Signal/slot connections need lambda for arguments
- Thread safety: never modify JobQueue without lock
- Qt signals must use pyqtSignal, not regular Python
