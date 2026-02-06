"""Tests for models/job_queue.py - job queue management."""

import pytest
from datetime import datetime
from unittest.mock import Mock

from models.job_queue import QueuedJob
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
