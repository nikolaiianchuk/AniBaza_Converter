# Render Queue Feature

## Overview

The render queue feature allows users to configure and queue multiple render jobs for batch processing. Jobs are processed sequentially in the order specified by the user.

## Architecture

### Components

- **JobQueue** (`models/job_queue.py`): Thread-safe queue data structure
- **QueuedJob** (`models/job_queue.py`): Wrapper around RenderJob with queue metadata
- **JobStatus** (`models/enums.py`): Enum for job states (WAITING, RUNNING, COMPLETED, FAILED, CANCELLED)
- **JobQueueWidget** (`widgets/job_queue_widget.py`): UI component for displaying queue
- **JobListItem** (`widgets/job_queue_widget.py`): Individual job display widget
- **QueueProcessor** (`threads/QueueProcessor.py`): Background thread for sequential processing

### Data Flow

1. User configures render settings in UI
2. Click "Add to Queue" → Create RenderJob → Add to JobQueue → Display in widget → Clear UI
3. Click "Start":
   - If queue has waiting jobs → Start QueueProcessor
   - If queue is empty → Start immediate render (legacy behavior)
4. QueueProcessor:
   - Get next WAITING job
   - Update status to RUNNING
   - Execute render
   - Update status (COMPLETED/FAILED/CANCELLED)
   - Repeat until no waiting jobs remain

## API Reference

### JobQueue

```python
class JobQueue:
    def add(self, job: RenderJob) -> str:
        """Add job to queue, returns unique job ID."""

    def remove(self, job_id: str) -> bool:
        """Remove job if not RUNNING. Returns True if removed."""

    def move_up(self, job_id: str) -> bool:
        """Move job up in queue if WAITING. Returns True if moved."""

    def move_down(self, job_id: str) -> bool:
        """Move job down in queue if WAITING. Returns True if moved."""

    def update_status(self, job_id: str, status: JobStatus, error: Optional[str] = None):
        """Update job status and optional error message."""

    def get_next_waiting(self) -> Optional[QueuedJob]:
        """Get next WAITING job for processing."""

    def has_waiting_jobs(self) -> bool:
        """Check if any WAITING jobs exist."""

    def clear_completed(self):
        """Remove all COMPLETED, FAILED, and CANCELLED jobs."""

    def get_all_jobs(self) -> list[QueuedJob]:
        """Get copy of all jobs for display."""
```

### QueueProcessor Signals

- `job_started(str)`: Emitted when job processing starts (job_id)
- `job_completed(str)`: Emitted when job completes successfully (job_id)
- `job_failed(str, str)`: Emitted when job fails (job_id, error_message)
- `job_cancelled(str)`: Emitted when job is cancelled (job_id)
- `queue_finished()`: Emitted when all jobs are processed

### JobQueueWidget Signals

- `job_removed(str)`: Emitted when user removes job (job_id)
- `job_moved(str, str)`: Emitted when user moves job (job_id, direction: "up"/"down")
- `job_cancelled(str)`: Emitted when user cancels job (job_id)
- `clear_completed_clicked()`: Emitted when user clicks Clear Completed button

## Testing

The render queue feature has comprehensive test coverage:

- **Unit tests**: 55 tests for JobQueue, JobQueueWidget, and QueueProcessor
- **Integration tests**: 10 tests for mainWindow integration and workflow
- **Total**: 65 tests specifically for render queue functionality

Run tests:
```bash
# All tests
pytest tests/

# Queue-specific tests only
pytest tests/test_job_queue.py tests/test_job_queue_widget.py tests/test_queue_processor.py tests/test_queue_integration.py
```

## User Guide

### Using the Queue

1. **Add Jobs to Queue**
   - Configure your render settings (video, audio, subtitle files)
   - Set the episode name
   - Click "Add to Queue" to add the job to the processing queue
   - Your settings will be cleared, allowing you to configure the next job

2. **Manage Queue**
   - View all queued jobs in the queue panel
   - Reorder waiting jobs using the up/down arrow buttons
   - Remove waiting jobs using the remove (×) button
   - Jobs show their current status: Waiting, Running, Completed, Failed, or Cancelled

3. **Process Queue**
   - Click "Start" to begin processing jobs sequentially
   - Add more jobs while processing is active
   - Click "Stop" to cancel the current job and pause the queue
   - Click "Start" again to resume from the next waiting job

4. **Queue Management**
   - Jobs process one at a time in order
   - Running jobs cannot be removed or reordered
   - Completed, failed, and cancelled jobs can be removed individually
   - Use "Clear Completed" to remove all finished jobs at once

### Queue Behavior

- **Empty Queue**: When the queue is empty, the Start button works as before (immediate render)
- **Active Queue**: When jobs are queued, the Start button processes the queue sequentially
- **Cancellation**: Clicking Stop during queue processing cancels the current job and pauses the queue
- **Error Handling**: If a job fails, it's marked as Failed and the queue continues to the next job

### Status Icons

- ⏱️ **Waiting**: Job is queued and waiting to be processed
- 🔄 **Running**: Job is currently being processed
- ✅ **Completed**: Job finished successfully
- ❌ **Failed**: Job encountered an error
- ⏹️ **Cancelled**: Job was manually stopped

## Limitations

- Queue is temporary (not persisted between app sessions)
- Jobs process sequentially (one at a time)
- Cannot modify job settings after adding to queue
- Cannot reorder or remove running jobs

## Future Enhancements

Potential improvements for future versions:

- Save/load queue to disk for persistence
- Parallel processing (multiple jobs at once)
- Drag-and-drop reordering in UI
- Edit queued job settings
- Job templates for quick configuration
- Progress bars and time estimates
- Queue statistics (total time, success rate)
