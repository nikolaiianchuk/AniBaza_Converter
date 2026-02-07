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
    """Test run method - sequential job processing."""

    def test_run_processes_jobs_sequentially(self, qapp):
        """run() processes waiting jobs sequentially from queue."""
        from unittest.mock import patch
        from PyQt5.QtCore import QEventLoop, QTimer

        queue = JobQueue()
        processor = QueueProcessor(queue)

        # Add two jobs to the queue
        job1 = Mock()
        job2 = Mock()
        job1_id = queue.add(job1)
        job2_id = queue.add(job2)

        # Mock RenderThread to simulate successful execution
        with patch('threads.RenderThread.ThreadClassRender') as MockRenderThread:
            mock_thread1 = Mock()
            mock_thread2 = Mock()

            # Simulate thread finishing immediately
            def run_and_finish(thread):
                thread.finished.emit()

            mock_thread1.run = Mock()
            mock_thread2.run = Mock()
            # Set _cancelled to False to indicate successful completion
            mock_thread1._cancelled = False
            mock_thread2._cancelled = False
            MockRenderThread.side_effect = [mock_thread1, mock_thread2]

            # Track signal emissions
            started_jobs = []
            completed_jobs = []
            processor.job_started.connect(lambda job_id: started_jobs.append(job_id))
            processor.job_completed.connect(lambda job_id: completed_jobs.append(job_id))

            # Run the processor
            processor.run()

            # Both jobs should have been started
            assert len(started_jobs) == 2
            assert job1_id in started_jobs
            assert job2_id in started_jobs

            # Jobs should be marked as completed
            jobs = queue.get_all_jobs()
            assert jobs[0].status == JobStatus.COMPLETED
            assert jobs[1].status == JobStatus.COMPLETED

    def test_run_handles_job_failure(self, qapp):
        """run() handles job failures and emits job_failed signal."""
        from unittest.mock import patch

        queue = JobQueue()
        processor = QueueProcessor(queue)

        # Add a job that will fail
        job = Mock()
        job_id = queue.add(job)

        # Mock RenderThread to simulate failure
        with patch('threads.RenderThread.ThreadClassRender') as MockRenderThread:
            mock_thread = Mock()
            mock_thread.run.side_effect = Exception("Encoding error")
            MockRenderThread.return_value = mock_thread

            # Track signal emissions
            failed_jobs = []
            error_messages = []
            processor.job_failed.connect(lambda job_id, msg: (failed_jobs.append(job_id), error_messages.append(msg)))

            # Run the processor
            processor.run()

            # Job should have failed
            assert len(failed_jobs) == 1
            assert failed_jobs[0] == job_id
            assert "Encoding error" in error_messages[0]

            # Job status should be updated to FAILED
            jobs = queue.get_all_jobs()
            assert jobs[0].status == JobStatus.FAILED
            assert jobs[0].error_message is not None

    def test_run_handles_cancellation(self, qapp):
        """run() handles cancellation and emits job_cancelled signal."""
        from unittest.mock import patch

        queue = JobQueue()
        processor = QueueProcessor(queue)

        # Add two jobs
        job1 = Mock()
        job2 = Mock()
        job1_id = queue.add(job1)
        job2_id = queue.add(job2)

        # Mock RenderThread
        with patch('threads.RenderThread.ThreadClassRender') as MockRenderThread:
            mock_thread = Mock()
            MockRenderThread.return_value = mock_thread

            # Set cancelled flag after first job starts
            cancelled_jobs = []

            def on_job_started(job_id):
                if job_id == job1_id:
                    processor.cancel_current_job()

            processor.job_started.connect(on_job_started)
            processor.job_cancelled.connect(lambda job_id: cancelled_jobs.append(job_id))

            # Run the processor
            processor.run()

            # First job should be cancelled
            assert len(cancelled_jobs) == 1
            assert cancelled_jobs[0] == job1_id

            # Job status should be updated to CANCELLED
            jobs = queue.get_all_jobs()
            assert jobs[0].status == JobStatus.CANCELLED


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
