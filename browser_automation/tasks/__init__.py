"""Browser automation tasks package."""
from browser_automation.tasks.base import Task, TaskCredentials
from browser_automation.tasks.login_task import LoginTask

__all__ = [
    "Task",
    "TaskCredentials",
    "LoginTask",
]
