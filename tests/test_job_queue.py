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

    def test_remove_waiting_job_succeeds(self):
        """Can remove job with WAITING status."""
        queue = JobQueue()
        job_id = queue.add(Mock())

        result = queue.remove(job_id)

        assert result is True
        assert len(queue.get_all_jobs()) == 0

    def test_remove_nonexistent_job_fails(self):
        """Cannot remove job that doesn't exist."""
        queue = JobQueue()
        queue.add(Mock())

        result = queue.remove("nonexistent-id")

        assert result is False
        assert len(queue.get_all_jobs()) == 1

    def test_remove_running_job_fails(self):
        """Cannot remove job with RUNNING status."""
        queue = JobQueue()
        job_id = queue.add(Mock())

        # Change status to RUNNING
        jobs = queue.get_all_jobs()
        jobs[0].status = JobStatus.RUNNING

        result = queue.remove(job_id)

        assert result is False
        assert len(queue.get_all_jobs()) == 1

    def test_remove_completed_job_succeeds(self):
        """Can remove job with COMPLETED status."""
        queue = JobQueue()
        job_id = queue.add(Mock())

        # Change status to COMPLETED
        jobs = queue.get_all_jobs()
        jobs[0].status = JobStatus.COMPLETED

        result = queue.remove(job_id)

        assert result is True
        assert len(queue.get_all_jobs()) == 0

    def test_move_up_waiting_job(self):
        """Can move WAITING job up in queue."""
        queue = JobQueue()
        id1 = queue.add(Mock(name="job1"))
        id2 = queue.add(Mock(name="job2"))
        id3 = queue.add(Mock(name="job3"))

        # Move job2 up (should swap with job1)
        result = queue.move_up(id2)

        assert result is True
        jobs = queue.get_all_jobs()
        assert jobs[0].id == id2
        assert jobs[1].id == id1
        assert jobs[2].id == id3

    def test_move_down_waiting_job(self):
        """Can move WAITING job down in queue."""
        queue = JobQueue()
        id1 = queue.add(Mock(name="job1"))
        id2 = queue.add(Mock(name="job2"))
        id3 = queue.add(Mock(name="job3"))

        # Move job2 down (should swap with job3)
        result = queue.move_down(id2)

        assert result is True
        jobs = queue.get_all_jobs()
        assert jobs[0].id == id1
        assert jobs[1].id == id3
        assert jobs[2].id == id2

    def test_move_up_first_job_fails(self):
        """Cannot move first job up."""
        queue = JobQueue()
        id1 = queue.add(Mock(name="job1"))
        id2 = queue.add(Mock(name="job2"))

        # Try to move first job up
        result = queue.move_up(id1)

        assert result is False
        jobs = queue.get_all_jobs()
        assert jobs[0].id == id1
        assert jobs[1].id == id2

    def test_move_down_last_job_fails(self):
        """Cannot move last job down."""
        queue = JobQueue()
        id1 = queue.add(Mock(name="job1"))
        id2 = queue.add(Mock(name="job2"))

        # Try to move last job down
        result = queue.move_down(id2)

        assert result is False
        jobs = queue.get_all_jobs()
        assert jobs[0].id == id1
        assert jobs[1].id == id2

    def test_move_up_running_job_fails(self):
        """Cannot move RUNNING job."""
        queue = JobQueue()
        id1 = queue.add(Mock(name="job1"))
        id2 = queue.add(Mock(name="job2"))

        # Set job2 to RUNNING
        jobs = queue.get_all_jobs()
        jobs[1].status = JobStatus.RUNNING

        # Try to move running job up
        result = queue.move_up(id2)

        assert result is False
        jobs = queue.get_all_jobs()
        assert jobs[0].id == id1
        assert jobs[1].id == id2

    def test_move_down_running_job_fails(self):
        """Cannot move RUNNING job."""
        queue = JobQueue()
        id1 = queue.add(Mock(name="job1"))
        id2 = queue.add(Mock(name="job2"))

        # Set job1 to RUNNING
        jobs = queue.get_all_jobs()
        jobs[0].status = JobStatus.RUNNING

        # Try to move running job down
        result = queue.move_down(id1)

        assert result is False
        jobs = queue.get_all_jobs()
        assert jobs[0].id == id1
        assert jobs[1].id == id2
