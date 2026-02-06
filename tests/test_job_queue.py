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
