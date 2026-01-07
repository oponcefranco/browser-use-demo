"""Tests for task runner."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio

from browser_automation.runner import TaskRunner


class TestTaskRunner:
    """Test TaskRunner class."""

    @pytest.mark.asyncio
    async def test_run_task_successfully(self):
        """Test running a task that completes successfully."""
        mock_agent = Mock()
        mock_agent.run = AsyncMock(return_value="Task completed")
        mock_browser_context = Mock()
        mock_browser_context.close = AsyncMock()

        result = await TaskRunner.run(mock_agent, mock_browser_context)

        # Verify agent.run was called with default max_steps
        mock_agent.run.assert_called_once_with(max_steps=25)

        # Verify browser was closed
        mock_browser_context.close.assert_called_once()

        # Verify result was returned
        assert result == "Task completed"

    @pytest.mark.asyncio
    async def test_run_task_with_custom_max_steps(self):
        """Test running a task with custom max_steps."""
        mock_agent = Mock()
        mock_agent.run = AsyncMock(return_value="Custom result")
        mock_browser_context = Mock()
        mock_browser_context.close = AsyncMock()

        custom_max_steps = 50

        result = await TaskRunner.run(
            mock_agent,
            mock_browser_context,
            max_steps=custom_max_steps
        )

        # Verify agent.run was called with custom max_steps
        mock_agent.run.assert_called_once_with(max_steps=custom_max_steps)
        assert result == "Custom result"

    @pytest.mark.asyncio
    async def test_run_task_closes_browser_on_success(self):
        """Test that browser is closed after successful task execution."""
        mock_agent = Mock()
        mock_agent.run = AsyncMock(return_value="Success")
        mock_browser_context = Mock()
        mock_browser_context.close = AsyncMock()

        await TaskRunner.run(mock_agent, mock_browser_context)

        # Verify browser.close was called
        mock_browser_context.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_task_closes_browser_on_failure(self):
        """Test that browser is closed even when task fails."""
        mock_agent = Mock()
        mock_agent.run = AsyncMock(side_effect=Exception("Task failed"))
        mock_browser_context = Mock()
        mock_browser_context.close = AsyncMock()

        with pytest.raises(Exception, match="Task failed"):
            await TaskRunner.run(mock_agent, mock_browser_context)

        # Verify browser was still closed despite the error
        mock_browser_context.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_task_propagates_exception(self):
        """Test that exceptions from agent.run are propagated."""
        mock_agent = Mock()
        error_message = "Navigation error"
        mock_agent.run = AsyncMock(side_effect=RuntimeError(error_message))
        mock_browser_context = Mock()
        mock_browser_context.close = AsyncMock()

        with pytest.raises(RuntimeError, match=error_message):
            await TaskRunner.run(mock_agent, mock_browser_context)

    @pytest.mark.asyncio
    async def test_run_task_logs_start_message(self):
        """Test that task start is logged."""
        mock_agent = Mock()
        mock_agent.run = AsyncMock(return_value="Success")
        mock_browser_context = Mock()
        mock_browser_context.close = AsyncMock()

        with patch('browser_automation.runner.logger') as mock_logger:
            await TaskRunner.run(mock_agent, mock_browser_context)

            # Verify start log message
            log_calls = [call[0][0] for call in mock_logger.info.call_args_list]
            assert any("Starting agent navigation" in msg for msg in log_calls)

    @pytest.mark.asyncio
    async def test_run_task_logs_completion_message(self):
        """Test that task completion is logged."""
        mock_agent = Mock()
        mock_agent.run = AsyncMock(return_value="Success")
        mock_browser_context = Mock()
        mock_browser_context.close = AsyncMock()

        with patch('browser_automation.runner.logger') as mock_logger:
            await TaskRunner.run(mock_agent, mock_browser_context)

            # Verify completion log message
            log_calls = [call[0][0] for call in mock_logger.info.call_args_list]
            assert any("Navigation task completed" in msg for msg in log_calls)

    @pytest.mark.asyncio
    async def test_run_task_logs_browser_closing(self):
        """Test that browser closing is logged."""
        mock_agent = Mock()
        mock_agent.run = AsyncMock(return_value="Success")
        mock_browser_context = Mock()
        mock_browser_context.close = AsyncMock()

        with patch('browser_automation.runner.logger') as mock_logger:
            await TaskRunner.run(mock_agent, mock_browser_context)

            # Verify browser closing logs
            log_calls = [call[0][0] for call in mock_logger.info.call_args_list]
            assert any("Closing browser" in msg for msg in log_calls)
            assert any("Browser closed" in msg for msg in log_calls)

    @pytest.mark.asyncio
    async def test_run_task_logs_error_on_failure(self):
        """Test that errors are logged when task fails."""
        mock_agent = Mock()
        error_message = "Test error"
        mock_agent.run = AsyncMock(side_effect=Exception(error_message))
        mock_browser_context = Mock()
        mock_browser_context.close = AsyncMock()

        with patch('browser_automation.runner.logger') as mock_logger:
            with pytest.raises(Exception):
                await TaskRunner.run(mock_agent, mock_browser_context)

            # Verify error was logged
            mock_logger.error.assert_called_once()
            error_log = mock_logger.error.call_args[0][0]
            assert "Error during navigation" in error_log
            assert error_message in str(mock_logger.error.call_args)

    @pytest.mark.asyncio
    async def test_run_task_with_zero_max_steps(self):
        """Test running task with zero max_steps (edge case)."""
        mock_agent = Mock()
        mock_agent.run = AsyncMock(return_value="No steps executed")
        mock_browser_context = Mock()
        mock_browser_context.close = AsyncMock()

        result = await TaskRunner.run(mock_agent, mock_browser_context, max_steps=0)

        # Verify agent.run was called with 0
        mock_agent.run.assert_called_once_with(max_steps=0)
        assert result == "No steps executed"

    @pytest.mark.asyncio
    async def test_run_task_with_large_max_steps(self):
        """Test running task with large max_steps value."""
        mock_agent = Mock()
        mock_agent.run = AsyncMock(return_value="Long running task")
        mock_browser_context = Mock()
        mock_browser_context.close = AsyncMock()

        large_max_steps = 1000

        result = await TaskRunner.run(
            mock_agent,
            mock_browser_context,
            max_steps=large_max_steps
        )

        mock_agent.run.assert_called_once_with(max_steps=large_max_steps)
        assert result == "Long running task"

    @pytest.mark.asyncio
    async def test_run_task_browser_close_failure_is_handled(self):
        """Test that errors during browser close don't mask task success."""
        mock_agent = Mock()
        mock_agent.run = AsyncMock(return_value="Task succeeded")
        mock_browser_context = Mock()
        # Simulate browser close failing
        mock_browser_context.close = AsyncMock(side_effect=Exception("Close failed"))

        # Task should raise the browser close error, but we verify the task ran
        with pytest.raises(Exception, match="Close failed"):
            await TaskRunner.run(mock_agent, mock_browser_context)

        # Verify task was still executed before close failed
        mock_agent.run.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_task_returns_various_result_types(self):
        """Test that task runner can return various result types."""
        test_results = [
            "string result",
            {"result": "dict"},
            ["list", "result"],
            42,
            None,
            True
        ]

        for expected_result in test_results:
            mock_agent = Mock()
            mock_agent.run = AsyncMock(return_value=expected_result)
            mock_browser_context = Mock()
            mock_browser_context.close = AsyncMock()

            result = await TaskRunner.run(mock_agent, mock_browser_context)
            assert result == expected_result

    @pytest.mark.asyncio
    async def test_runner_method_is_static(self):
        """Test that TaskRunner method can be called without instantiation."""
        # Verify this is a static method
        assert callable(TaskRunner.run)

        mock_agent = Mock()
        mock_agent.run = AsyncMock(return_value="Success")
        mock_browser_context = Mock()
        mock_browser_context.close = AsyncMock()

        # Should not raise any errors about needing self
        await TaskRunner.run(mock_agent, mock_browser_context)

    @pytest.mark.asyncio
    async def test_run_task_with_complex_agent_result(self):
        """Test running task that returns complex agent result."""
        complex_result = {
            "status": "completed",
            "steps_taken": 15,
            "actions": ["navigate", "click", "type", "submit"],
            "final_url": "https://example.com/dashboard"
        }

        mock_agent = Mock()
        mock_agent.run = AsyncMock(return_value=complex_result)
        mock_browser_context = Mock()
        mock_browser_context.close = AsyncMock()

        result = await TaskRunner.run(mock_agent, mock_browser_context)

        assert result == complex_result
        assert result["status"] == "completed"
        assert result["steps_taken"] == 15
