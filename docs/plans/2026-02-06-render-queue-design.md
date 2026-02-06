# Render Job Queue Feature Design

**Date:** 2026-02-06
**Status:** Approved

## Overview

Add a job queue system to AniBaza Converter, allowing users to configure multiple render jobs before processing. Users can add jobs to a queue, reorder them, and process them sequentially with a single "Start" button.

## Requirements Summary

- **Job Creation:** Configure parameters → "Add to Queue" → fields reset for next job
- **Queue Display:** Simple vertical list showing episode name and status
- **Reordering:** Up/Down arrow buttons for waiting jobs
- **Processing:** Sequential, one job at a time
- **Queue Management:** Add jobs and reorder waiting jobs while processing; can't modify running job
- **Cancellation:** Stop button cancels current job and pauses queue
- **Error Handling:** Failed jobs pause queue with continue/stop dialog
- **Persistence:** Queue is temporary (lost on app close)
- **UI Placement:** Below configuration area in main window
- **Start Button:** Smart behavior - process current settings if queue empty, else process queue
- **Completed Jobs:** Keep in list with "Completed" status, "Clear Completed" button
- **Job Display:** Minimal - just episode name and status

## Architecture

### Core Components

1. **JobQueue Model** (`models/job_queue.py`)
   - Thread-safe job list management
   - Operations: add, remove, reorder, get_next_waiting, update_status, clear_completed

2. **JobQueueWidget** (`widgets/job_queue_widget.py`)
   - PyQt5 QWidget displaying job list
   - Custom list items with status icons and action buttons
   - Emits signals for user actions

3. **QueueProcessor** (`threads/QueueProcessor.py`)
   - QThread processing jobs sequentially
   - Wraps existing RenderThread
   - Handles cancellation and error pausing

4. **Job Status Enum** (`models/enums.py`)
   - Add JobStatus: WAITING, RUNNING, COMPLETED, FAILED, CANCELLED

### Data Flow

```
User fills UI → "Add to Queue" → Create RenderJob from UI state
→ Add to JobQueue → Display in JobQueueWidget → Clear UI

User clicks "Start":
  - If queue empty → Process current settings immediately (old behavior)
  - If queue has jobs → Start QueueProcessor

QueueProcessor:
  Get next WAITING job → Update to RUNNING → Execute RenderThread
  → Update status (COMPLETED/FAILED/CANCELLED) → Get next job → Repeat

Error/Cancellation → Pause queue → Show dialog → User decides continue/stop
```

## Data Model

### QueuedJob Dataclass

```python
@dataclass
class QueuedJob:
    """Wrapper around RenderJob with queue metadata."""
    job: RenderJob
    id: str  # Unique identifier (UUID)
    status: JobStatus = JobStatus.WAITING
    created_at: datetime = field(default_factory=datetime.now)
    error_message: Optional[str] = None
```

### JobQueue Class

```python
class JobQueue:
    """Thread-safe job queue manager."""

    def __init__(self):
        self._jobs: list[QueuedJob] = []
        self._lock = threading.Lock()

    def add(self, job: RenderJob) -> str:
        """Add job, return ID."""

    def remove(self, job_id: str) -> bool:
        """Remove job if not RUNNING."""

    def move_up(self, job_id: str) -> bool:
        """Move job up if WAITING."""

    def move_down(self, job_id: str) -> bool:
        """Move job down if WAITING."""

    def get_next_waiting(self) -> Optional[QueuedJob]:
        """Get next WAITING job."""

    def update_status(self, job_id: str, status: JobStatus, error: str = None):
        """Update job status."""

    def clear_completed(self):
        """Remove all COMPLETED jobs."""

    def has_waiting_jobs(self) -> bool:
        """Check if any WAITING jobs exist."""

    def get_all_jobs(self) -> list[QueuedJob]:
        """Get copy of all jobs for display."""
```

**Thread Safety:** All operations protected by `threading.Lock`. Jobs can only be reordered or removed if status is `WAITING`.

## UI Components

### JobListItem Widget

Custom widget for each job in the list:

```
[●] Episode 01 - Subtitle    [↑] [↓] [×]
```

- **Status Icon (●):** Color-coded by status
  - Gray = WAITING
  - Blue = RUNNING
  - Green = COMPLETED
  - Red = FAILED
  - Orange = CANCELLED

- **Action Buttons:**
  - WAITING jobs: show [↑] [↓] [×] (move up, move down, remove)
  - RUNNING jobs: show [⏹️] (stop)
  - COMPLETED/FAILED/CANCELLED: show [×] (remove)

### JobQueueWidget

```python
class JobQueueWidget(QWidget):
    """Main queue display widget."""

    # Signals
    job_removed = pyqtSignal(str)  # job_id
    job_moved = pyqtSignal(str, str)  # job_id, direction ("up"/"down")
    job_cancelled = pyqtSignal(str)  # job_id

    def __init__(self):
        # QListWidget for jobs
        # "Clear Completed" button at bottom

    def update_jobs(self, jobs: list[QueuedJob]):
        """Refresh display from queue state."""
```

### MainWindow Integration

**New UI Elements:**
- "Add to Queue" button next to existing file inputs
- JobQueueWidget below configuration area
- Existing "Start/Stop" buttons repurposed

**Button Logic:**

```python
def on_start_clicked(self):
    if self.job_queue.has_waiting_jobs():
        # Start queue processing
        self.queue_processor.start()
        self.ui.render_start_button.hide()
        self.ui.render_stop_button.show()
    else:
        # Old behavior: process current settings immediately
        self.start_immediate_render()

def on_add_to_queue_clicked(self):
    # 1. Validate current UI inputs
    # 2. Create RenderPaths from UI state
    # 3. Create RenderJob from config + paths
    # 4. Add to queue: job_id = self.job_queue.add(job)
    # 5. Clear/reset UI inputs for next job
    # 6. Update queue widget: self.queue_widget.update_jobs(self.job_queue.get_all_jobs())

def on_stop_clicked(self):
    # Cancel current job and pause queue
    self.queue_processor.cancel_current_job()
```

**State Management:**
- Allow adding to queue while processing (user confirmed)
- Disable reordering/removal for RUNNING jobs
- Stop button cancels current job AND pauses queue

## Queue Processor

```python
class QueueProcessor(QThread):
    """Processes jobs from queue sequentially."""

    # Signals
    job_started = pyqtSignal(str)  # job_id
    job_completed = pyqtSignal(str)  # job_id
    job_failed = pyqtSignal(str, str)  # job_id, error_message
    job_cancelled = pyqtSignal(str)  # job_id
    queue_finished = pyqtSignal()

    def __init__(self, queue: JobQueue, runner: ProcessRunner, config):
        self._queue = queue
        self._runner = runner
        self._config = config
        self._current_render_thread: Optional[ThreadClassRender] = None
        self._should_stop = False
        self._paused = False

    def cancel_current_job(self):
        """Stop the running job."""
        if self._current_render_thread:
            self._current_render_thread.stop()
            self._should_stop = True

    def resume(self):
        """Resume processing after pause."""
        self._paused = False

    def run(self):
        while not self._paused:
            job = self._queue.get_next_waiting()
            if not job:
                break

            self._queue.update_status(job.id, JobStatus.RUNNING)
            self.job_started.emit(job.id)

            try:
                # Create and execute RenderThread
                self._current_render_thread = ThreadClassRender(
                    self._config, self._runner, job.job
                )
                self._current_render_thread.run()  # Blocking call

                if self._should_stop:
                    self._queue.update_status(job.id, JobStatus.CANCELLED)
                    self.job_cancelled.emit(job.id)
                    self._should_stop = False
                    self._paused = True  # Pause queue after cancel
                    break
                else:
                    self._queue.update_status(job.id, JobStatus.COMPLETED)
                    self.job_completed.emit(job.id)

            except Exception as e:
                error_msg = str(e)
                self._queue.update_status(job.id, JobStatus.FAILED, error_msg)
                self.job_failed.emit(job.id, error_msg)
                self._paused = True  # Pause queue on error
                break

            finally:
                self._current_render_thread = None

        if not self._paused:
            self.queue_finished.emit()
```

## Error Handling

### Job Failure Flow

1. RenderThread raises exception
2. QueueProcessor catches exception
3. Update job status to FAILED with error message
4. Emit `job_failed` signal
5. Pause queue processing
6. MainWindow shows dialog:
   ```
   Job failed: Episode 01
   Error: {error_message}

   Continue with next job?  [Yes] [No]
   ```
7. User choice:
   - **Yes:** Call `queue_processor.resume()`, continue to next job
   - **No:** Keep paused, user can restart queue later

### Cancellation Flow

1. User clicks Stop button on running job
2. MainWindow calls `queue_processor.cancel_current_job()`
3. QueueProcessor calls `render_thread.stop()`
4. Job status updated to CANCELLED
5. Queue pauses (same as error case)
6. User can restart queue or clear cancelled job

## Testing Strategy

### Unit Tests

**`tests/test_job_queue.py`** - JobQueue operations
- `test_add_job_returns_id`
- `test_remove_waiting_job_succeeds`
- `test_remove_running_job_fails`
- `test_move_up_waiting_job`
- `test_move_up_first_job_noop`
- `test_move_down_waiting_job`
- `test_move_down_last_job_noop`
- `test_move_running_job_fails`
- `test_get_next_waiting_skips_completed`
- `test_update_status_thread_safe`
- `test_clear_completed_removes_only_completed`
- `test_has_waiting_jobs`

**`tests/test_queue_processor.py`** - QueueProcessor logic
- `test_process_single_job_successfully`
- `test_process_multiple_jobs_sequentially`
- `test_cancel_current_job_pauses_queue`
- `test_failed_job_pauses_queue`
- `test_resume_after_failure_continues`
- `test_empty_queue_finishes_immediately`
- `test_signals_emitted_correctly`

**`tests/test_job_queue_widget.py`** - UI widget (pytest-qt)
- `test_display_updates_on_new_jobs`
- `test_waiting_job_shows_move_remove_buttons`
- `test_running_job_shows_stop_button`
- `test_completed_job_shows_remove_button`
- `test_move_up_emits_signal`
- `test_move_down_emits_signal`
- `test_remove_emits_signal`
- `test_cancel_emits_signal`
- `test_clear_completed_button`

### Integration Tests

**`tests/test_queue_integration.py`**
- `test_full_flow_add_process_complete`
- `test_add_jobs_while_processing`
- `test_cancel_job_and_continue`
- `test_failed_job_dialog_continue`
- `test_failed_job_dialog_stop`
- `test_empty_queue_immediate_render`
- `test_reorder_jobs_before_start`

### Manual Testing Checklist

- [ ] Add 3 jobs with different configurations
- [ ] Reorder jobs before starting (move up, move down, boundaries)
- [ ] Start queue and verify sequential processing
- [ ] Add new jobs while queue is processing
- [ ] Cancel running job (2nd of 3), verify pause
- [ ] Simulate failed job, test continue/stop dialog
- [ ] Clear completed jobs
- [ ] Empty queue → Start button → Immediate render (old behavior)
- [ ] Verify status icons change colors correctly
- [ ] Verify buttons enable/disable based on job status

## Implementation Notes

### Backward Compatibility

- Existing immediate render flow preserved when queue is empty
- Start button behavior is smart: checks queue state first
- No changes to RenderThread or encoding logic
- Configuration and paths handling unchanged

### UI/UX Considerations

- **Status Colors:** Use standard color conventions (green=success, red=error, blue=active)
- **Button States:** Clear visual feedback for disabled buttons
- **Error Messages:** Show full error in dialog, truncate in list view
- **Progress:** Consider adding progress bar for running job (future enhancement)

### Future Enhancements (Out of Scope)

- Save/load queue to disk
- Parallel processing (multiple jobs at once)
- Drag-and-drop reordering
- Job templates for quick configuration
- Progress bars and time estimates
- Queue statistics (total time, success rate)

## Files to Create

```
models/job_queue.py          # JobQueue and QueuedJob classes
threads/QueueProcessor.py    # QueueProcessor thread
widgets/                     # New directory
widgets/__init__.py
widgets/job_queue_widget.py  # JobQueueWidget and JobListItem
tests/test_job_queue.py      # Unit tests for JobQueue
tests/test_queue_processor.py # Unit tests for QueueProcessor
tests/test_job_queue_widget.py # UI tests for widget
tests/test_queue_integration.py # Integration tests
```

## Files to Modify

```
models/enums.py              # Add JobStatus enum
windows/mainWindow.py        # Integrate queue widget and buttons
UI/normUI2.ui               # Add "Add to Queue" button (or programmatic)
```

## Success Criteria

- [ ] Users can add multiple jobs to queue
- [ ] Jobs process sequentially when Start is clicked
- [ ] Can reorder waiting jobs with arrow buttons
- [ ] Can cancel running job, pauses queue
- [ ] Failed jobs pause queue with continue/stop dialog
- [ ] Completed jobs remain visible with status
- [ ] Clear completed button works
- [ ] Empty queue preserves old immediate render behavior
- [ ] All tests pass (180 existing + ~30 new = 210+ total)
- [ ] No regressions in existing render functionality
