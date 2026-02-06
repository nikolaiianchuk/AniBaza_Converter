"""Tests for threads/QueueProcessor.py - queue processing thread."""

from unittest.mock import Mock, MagicMock, patch
import pytest

from models.enums import JobStatus
from models.job_queue import JobQueue, QueuedJob
from threads.QueueProcessor import QueueProcessor


class TestQueueProcessorSignals:
    """Test QueueProcessor signal definitions."""

    def test_has_job_started_signal(self, qapp):
        """QueueProcessor has job_started signal."""
        queue = JobQueue()
        processor = QueueProcessor(queue)

        assert hasattr(processor, 'job_started')

    def test_has_job_completed_signal(self, qapp):
        """QueueProcessor has job_completed signal."""
        queue = JobQueue()
        processor = QueueProcessor(queue)

        assert hasattr(processor, 'job_completed')

    def test_has_job_failed_signal(self, qapp):
        """QueueProcessor has job_failed signal."""
        queue = JobQueue()
        processor = QueueProcessor(queue)

        assert hasattr(processor, 'job_failed')

    def test_has_job_cancelled_signal(self, qapp):
        """QueueProcessor has job_cancelled signal."""
        queue = JobQueue()
        processor = QueueProcessor(queue)

        assert hasattr(processor, 'job_cancelled')

    def test_has_queue_finished_signal(self, qapp):
        """QueueProcessor has queue_finished signal."""
        queue = JobQueue()
        processor = QueueProcessor(queue)

        assert hasattr(processor, 'queue_finished')


class TestQueueProcessorInitialization:
    """Test QueueProcessor initialization."""

    def test_accepts_job_queue(self, qapp):
        """QueueProcessor accepts JobQueue in constructor."""
        queue = JobQueue()
        processor = QueueProcessor(queue)

        assert processor.queue is queue

    def test_initializes_with_no_current_job(self, qapp):
        """QueueProcessor starts with no current job."""
        queue = JobQueue()
        processor = QueueProcessor(queue)

        assert processor.current_job_id is None

    def test_initializes_not_cancelled(self, qapp):
        """QueueProcessor starts with cancelled=False."""
        queue = JobQueue()
        processor = QueueProcessor(queue)

        assert processor.cancelled is False


class TestQueueProcessorCancelCurrentJob:
    """Test cancel_current_job method."""

    def test_cancel_current_job_sets_cancelled_flag(self, qapp):
        """cancel_current_job sets cancelled flag to True."""
        queue = JobQueue()
        processor = QueueProcessor(queue)

        processor.cancel_current_job()

        assert processor.cancelled is True

    def test_cancel_current_job_when_no_current_job(self, qapp):
        """cancel_current_job works even when no job is running."""
        queue = JobQueue()
        processor = QueueProcessor(queue)

        # Should not raise exception
        processor.cancel_current_job()

        assert processor.cancelled is True
        assert processor.current_job_id is None

    def test_cancel_current_job_with_current_job_id(self, qapp):
        """cancel_current_job works when current_job_id is set."""
        queue = JobQueue()
        processor = QueueProcessor(queue)

        # Simulate having a current job
        processor.current_job_id = "test-job-123"

        processor.cancel_current_job()

        assert processor.cancelled is True
        assert processor.current_job_id == "test-job-123"  # ID preserved


class TestQueueProcessorResume:
    """Test resume method."""

    def test_resume_clears_cancelled_flag(self, qapp):
        """resume clears the cancelled flag."""
        queue = JobQueue()
        processor = QueueProcessor(queue)

        # Set cancelled first
        processor.cancelled = True

        processor.resume()

        assert processor.cancelled is False

    def test_resume_when_not_cancelled(self, qapp):
        """resume works even when not cancelled."""
        queue = JobQueue()
        processor = QueueProcessor(queue)

        # Already not cancelled
        assert processor.cancelled is False

        processor.resume()

        assert processor.cancelled is False


class TestQueueProcessorRun:
    """Test run method (stub for now)."""

    def test_run_method_exists(self, qapp):
        """QueueProcessor has run method."""
        queue = JobQueue()
        processor = QueueProcessor(queue)

        assert hasattr(processor, 'run')
        assert callable(processor.run)

    def test_run_is_stub_for_now(self, qapp):
        """run method is a stub (does nothing or minimal work)."""
        queue = JobQueue()
        processor = QueueProcessor(queue)

        # Should not raise exception
        processor.run()

        # run() is a stub, so it should do nothing meaningful yet
        # In Task 10, this will be implemented with actual queue processing


class TestQueueProcessorThreadSafety:
    """Test thread-safe access to job queue."""

    def test_accesses_queue_safely(self, qapp):
        """QueueProcessor can access thread-safe queue."""
        queue = JobQueue()
        job_id = queue.add(Mock())

        processor = QueueProcessor(queue)

        # Should be able to access queue methods
        all_jobs = processor.queue.get_all_jobs()
        assert len(all_jobs) == 1
        assert all_jobs[0].id == job_id
