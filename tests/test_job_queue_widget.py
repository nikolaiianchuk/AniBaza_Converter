"""Tests for widgets/job_queue_widget.py - JobListItem widget."""

import pytest
from unittest.mock import Mock, MagicMock
from PyQt5.QtWidgets import QPushButton, QLabel, QHBoxLayout

from models.job_queue import QueuedJob
from models.enums import JobStatus
from widgets.job_queue_widget import JobListItem


class TestJobListItem:
    """Test JobListItem widget - displays a single job in the queue."""

    def test_create_waiting_job_item(self, qapp):
        """JobListItem shows status icon and action buttons for WAITING job."""
        mock_job = Mock()
        mock_job.job.episode_name = "Episode 01"
        mock_job.id = "test-123"
        mock_job.status = JobStatus.WAITING

        item = JobListItem(mock_job)

        # Should show episode name
        assert "Episode 01" in item.label.text()

        # Should show waiting icon/indicator
        assert "WAITING" in item.status_label.text() or "⏳" in item.status_label.text()

        # Should have move up, move down, and remove buttons
        assert item.move_up_button is not None
        assert item.move_down_button is not None
        assert item.remove_button is not None

        # Should NOT have stop button (only for RUNNING jobs)
        assert not hasattr(item, 'stop_button') or item.stop_button is None

    def test_create_running_job_item(self, qapp):
        """JobListItem shows stop button for RUNNING job."""
        mock_job = Mock()
        mock_job.job.episode_name = "Episode 02"
        mock_job.id = "test-456"
        mock_job.status = JobStatus.RUNNING

        item = JobListItem(mock_job)

        # Should show episode name
        assert "Episode 02" in item.label.text()

        # Should show running icon/indicator
        assert "RUNNING" in item.status_label.text() or "▶" in item.status_label.text()

        # Should have stop button
        assert item.stop_button is not None
        assert isinstance(item.stop_button, QPushButton)

        # Should NOT have move or remove buttons (cannot modify running job)
        assert not hasattr(item, 'move_up_button') or item.move_up_button is None
        assert not hasattr(item, 'move_down_button') or item.move_down_button is None
        assert not hasattr(item, 'remove_button') or item.remove_button is None

    def test_create_completed_job_item(self, qapp):
        """JobListItem shows remove button for COMPLETED job."""
        mock_job = Mock()
        mock_job.job.episode_name = "Episode 03"
        mock_job.id = "test-789"
        mock_job.status = JobStatus.COMPLETED

        item = JobListItem(mock_job)

        # Should show episode name
        assert "Episode 03" in item.label.text()

        # Should show completed icon/indicator
        assert "COMPLETED" in item.status_label.text() or "✓" in item.status_label.text()

        # Should have remove button only
        assert item.remove_button is not None

        # Should NOT have move or stop buttons
        assert not hasattr(item, 'move_up_button') or item.move_up_button is None
        assert not hasattr(item, 'move_down_button') or item.move_down_button is None
        assert not hasattr(item, 'stop_button') or item.stop_button is None

    def test_create_failed_job_item(self, qapp):
        """JobListItem shows error message for FAILED job."""
        mock_job = Mock()
        mock_job.job.episode_name = "Episode 04"
        mock_job.id = "test-abc"
        mock_job.status = JobStatus.FAILED
        mock_job.error_message = "FFmpeg process failed"

        item = JobListItem(mock_job)

        # Should show episode name
        assert "Episode 04" in item.label.text()

        # Should show failed icon/indicator
        assert "FAILED" in item.status_label.text() or "✗" in item.status_label.text()

        # Should show error message (either in label or tooltip)
        widget_text = item.label.text() + str(item.label.toolTip())
        assert "FFmpeg process failed" in widget_text or "error" in widget_text.lower()

        # Should have remove button
        assert item.remove_button is not None

    def test_create_cancelled_job_item(self, qapp):
        """JobListItem shows cancelled status."""
        mock_job = Mock()
        mock_job.job.episode_name = "Episode 05"
        mock_job.id = "test-def"
        mock_job.status = JobStatus.CANCELLED

        item = JobListItem(mock_job)

        # Should show episode name
        assert "Episode 05" in item.label.text()

        # Should show cancelled icon/indicator
        assert "CANCELLED" in item.status_label.text() or "⊗" in item.status_label.text()

        # Should have remove button
        assert item.remove_button is not None

    def test_move_up_button_emits_signal(self, qapp):
        """Move up button emits signal with job ID."""
        mock_job = Mock()
        mock_job.job.episode_name = "Episode 06"
        mock_job.id = "test-signal-up"
        mock_job.status = JobStatus.WAITING

        item = JobListItem(mock_job)

        # Connect signal to mock
        mock_handler = Mock()
        item.move_up_requested.connect(mock_handler)

        # Click move up button
        item.move_up_button.click()

        # Should emit signal with job ID
        mock_handler.assert_called_once_with("test-signal-up")

    def test_move_down_button_emits_signal(self, qapp):
        """Move down button emits signal with job ID."""
        mock_job = Mock()
        mock_job.job.episode_name = "Episode 07"
        mock_job.id = "test-signal-down"
        mock_job.status = JobStatus.WAITING

        item = JobListItem(mock_job)

        # Connect signal to mock
        mock_handler = Mock()
        item.move_down_requested.connect(mock_handler)

        # Click move down button
        item.move_down_button.click()

        # Should emit signal with job ID
        mock_handler.assert_called_once_with("test-signal-down")

    def test_remove_button_emits_signal(self, qapp):
        """Remove button emits signal with job ID."""
        mock_job = Mock()
        mock_job.job.episode_name = "Episode 08"
        mock_job.id = "test-signal-remove"
        mock_job.status = JobStatus.WAITING

        item = JobListItem(mock_job)

        # Connect signal to mock
        mock_handler = Mock()
        item.remove_requested.connect(mock_handler)

        # Click remove button
        item.remove_button.click()

        # Should emit signal with job ID
        mock_handler.assert_called_once_with("test-signal-remove")

    def test_stop_button_emits_signal(self, qapp):
        """Stop button emits signal with job ID for RUNNING job."""
        mock_job = Mock()
        mock_job.job.episode_name = "Episode 09"
        mock_job.id = "test-signal-stop"
        mock_job.status = JobStatus.RUNNING

        item = JobListItem(mock_job)

        # Connect signal to mock
        mock_handler = Mock()
        item.stop_requested.connect(mock_handler)

        # Click stop button
        item.stop_button.click()

        # Should emit signal with job ID
        mock_handler.assert_called_once_with("test-signal-stop")

    def test_widget_layout(self, qapp):
        """JobListItem has proper horizontal layout."""
        mock_job = Mock()
        mock_job.job.episode_name = "Episode 10"
        mock_job.id = "test-layout"
        mock_job.status = JobStatus.WAITING

        item = JobListItem(mock_job)

        # Should use horizontal layout
        assert item.layout() is not None
        assert isinstance(item.layout(), QHBoxLayout)

    def test_status_icons_are_distinct(self, qapp):
        """Each job status has a distinct icon/text."""
        statuses = [
            JobStatus.WAITING,
            JobStatus.RUNNING,
            JobStatus.COMPLETED,
            JobStatus.FAILED,
            JobStatus.CANCELLED
        ]

        status_texts = []
        for status in statuses:
            mock_job = Mock()
            mock_job.job.episode_name = "Test"
            mock_job.id = "test-id"
            mock_job.status = status

            item = JobListItem(mock_job)
            status_texts.append(item.status_label.text())

        # All status texts should be unique
        assert len(status_texts) == len(set(status_texts))


class TestJobQueueWidget:
    """Test JobQueueWidget container - displays list of jobs with controls."""

    def test_create_empty_queue_widget(self, qapp):
        """JobQueueWidget can be created with empty job list."""
        from widgets.job_queue_widget import JobQueueWidget

        widget = JobQueueWidget()

        # Should have QListWidget
        assert hasattr(widget, 'list_widget')
        assert widget.list_widget is not None

        # Should have clear completed button
        assert hasattr(widget, 'clear_completed_button')
        assert widget.clear_completed_button is not None
        assert isinstance(widget.clear_completed_button, QPushButton)

    def test_display_jobs_in_list(self, qapp):
        """JobQueueWidget displays list of jobs."""
        from widgets.job_queue_widget import JobQueueWidget

        # Create mock jobs
        mock_job1 = Mock()
        mock_job1.job.episode_name = "Episode 01"
        mock_job1.id = "job-1"
        mock_job1.status = JobStatus.WAITING

        mock_job2 = Mock()
        mock_job2.job.episode_name = "Episode 02"
        mock_job2.id = "job-2"
        mock_job2.status = JobStatus.RUNNING

        jobs = [mock_job1, mock_job2]

        widget = JobQueueWidget()
        widget.update_jobs(jobs)

        # Should display 2 items in list
        assert widget.list_widget.count() == 2

    def test_clear_button_emits_signal(self, qapp):
        """Clear completed button emits clear_completed signal."""
        from widgets.job_queue_widget import JobQueueWidget

        widget = JobQueueWidget()

        # Connect signal to mock
        mock_handler = Mock()
        widget.clear_completed_requested.connect(mock_handler)

        # Click clear button
        widget.clear_completed_button.click()

        # Should emit signal
        mock_handler.assert_called_once()

    def test_job_actions_propagate_signals(self, qapp):
        """Job item actions propagate through JobQueueWidget signals."""
        from widgets.job_queue_widget import JobQueueWidget

        # Create mock job
        mock_job = Mock()
        mock_job.job.episode_name = "Episode 01"
        mock_job.id = "test-job-123"
        mock_job.status = JobStatus.WAITING

        widget = JobQueueWidget()
        widget.update_jobs([mock_job])

        # Connect signals to mocks
        move_up_handler = Mock()
        move_down_handler = Mock()
        remove_handler = Mock()
        stop_handler = Mock()

        widget.move_up_requested.connect(move_up_handler)
        widget.move_down_requested.connect(move_down_handler)
        widget.remove_requested.connect(remove_handler)
        widget.stop_requested.connect(stop_handler)

        # Get the JobListItem widget from the list
        list_item = widget.list_widget.item(0)
        job_item_widget = widget.list_widget.itemWidget(list_item)

        # Trigger move up action
        job_item_widget.move_up_requested.emit("test-job-123")
        move_up_handler.assert_called_once_with("test-job-123")

        # Trigger move down action
        job_item_widget.move_down_requested.emit("test-job-123")
        move_down_handler.assert_called_once_with("test-job-123")

        # Trigger remove action
        job_item_widget.remove_requested.emit("test-job-123")
        remove_handler.assert_called_once_with("test-job-123")
