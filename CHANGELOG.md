# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Render job queue system for batch processing
  - Add multiple render jobs before processing
  - Visual queue display with status indicators (Waiting, Running, Completed, Failed, Cancelled)
  - Reorder waiting jobs with up/down buttons
  - Sequential job processing with QueueProcessor thread
  - Queue management during processing (add, cancel, resume)
  - Clear completed jobs functionality
  - Smart Start button (queue vs immediate render)
  - Smart Stop button (cancel queue job vs kill immediate render)
  - Thread-safe JobQueue model with comprehensive API
  - JobQueueWidget with JobListItem components for UI display
  - Full integration with existing MainWindow and rendering system
  - Comprehensive test coverage (65 tests for queue functionality)

### Changed
- Start button now processes queue when jobs are waiting, or performs immediate render when queue is empty
- Stop button now cancels current queue job when processing queue, or kills render process when doing immediate render
- UI settings are now cleared after adding job to queue for convenient batch configuration

## [2.7.1] - 2025-01-XX

Previous releases...
