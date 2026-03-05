"""
Codegen Progress Adapter

Direct imports from Codegen SDK progress tracking - no reimplementation.
Provides progress tracking and task management for long-running operations.

Features:
- Progress tracking with callbacks
- Task management and cancellation
- Parallel execution monitoring
- User feedback for UX
"""

from codegen.sdk.codebase.progress.progress import Progress as _Progress
from codegen.sdk.codebase.progress.task import Task as _Task
from codegen.sdk.codebase.progress.stub_progress import StubProgress as _StubProgress
from codegen.sdk.codebase.progress.stub_task import StubTask as _StubTask

# Re-export with tier unification
# All progress tracking is now Community tier accessible

Progress = _Progress
"""
Progress tracker class - Community tier

Tracks progress of long-running operations with:
- Progress callbacks
- Percentage completion
- ETA calculation
- Cancellation support

Example:
    progress = Progress(total=100)
    for i in range(100):
        progress.update(1)
        if progress.cancelled:
            break
"""

Task = _Task
"""
Task class - Community tier

Represents a unit of work with:
- Task status (pending, running, completed, failed)
- Progress tracking
- Result storage
- Error handling

Example:
    task = Task("Parse codebase")
    task.start()
    # ... do work ...
    task.complete(result)
"""

StubProgress = _StubProgress
"""
Stub progress tracker - Community tier

No-op progress tracker for testing with:
- Same interface as Progress
- No actual tracking
- Useful for tests
"""

StubTask = _StubTask
"""
Stub task - Community tier

No-op task for testing with:
- Same interface as Task
- No actual execution
- Useful for tests
"""

__all__ = [
    'Progress',
    'Task',
    'StubProgress',
    'StubTask',
]

