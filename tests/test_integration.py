"""Integration tests for browser automation workflow."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from pydantic import SecretStr

from browser_automation.config import AppConfig, ConfigValidator
from browser_automation.browser_factory import BrowserFactory
from browser_automation.agent_factory import AgentFactory
from browser_automation.runner import TaskRunner
from browser_automation.tasks.login_task import LoginTask
from browser_automation.tasks.base import TaskCredentials


class TestConfigToRunnerIntegration:
    """Test integration between config loading and task execution."""

    def test_config_validation_before_browser_creation(self):
        """Test that config is validated before attempting to create browser."""
        # Invalid config (missing required fields)
        invalid_config = AppConfig(
            openai_api_key=None,
            chromium_path="/path/to/chromium",
            base_url="",
            auth_username=None,
            auth_password=None
        )

        # Validation should fail before we even try to create browser
        with pytest.raises(ValueError):
            ConfigValidator.validate(invalid_config)

    def test_valid_config_passes_validation(self):
        """Test that valid config passes validation."""
        valid_config = AppConfig(
            openai_api_key=SecretStr("sk-key"),
            chromium_path="/path/to/chromium",
            base_url="https://test.com",
            auth_username=SecretStr("user"),
            auth_password=SecretStr("pass")
        )

        # Should not raise
        ConfigValidator.validate(valid_config)

    def test_browser_context_creation_flow(self):
        """Test complete browser and context creation flow."""
        config = AppConfig(
            openai_api_key=SecretStr("sk-key"),
            chromium_path="/path/to/chromium",
            base_url="https://test.com",
            auth_username=SecretStr("user"),
            auth_password=SecretStr("pass")
        )

        with patch('browser_automation.browser_factory.Browser') as mock_browser_class, \
             patch('browser_automation.browser_factory.BrowserContext') as mock_context_class:

            mock_browser = Mock()
            mock_browser_class.return_value = mock_browser
            mock_context = Mock()
            mock_context_class.return_value = mock_context

            # Create browser
            browser = BrowserFactory.create_browser(config)
            assert browser == mock_browser

            # Create context from browser
            context = BrowserFactory.create_context(browser)
            assert context == mock_context


class TestTaskCreationIntegration:
    """Test integration between task creation and agent configuration."""

    def test_login_task_instructions_used_by_agent(self):
        """Test that login task instructions are properly passed to agent."""
        config = AppConfig(
            openai_api_key=SecretStr("sk-key"),
            chromium_path="/path/to/chromium",
            base_url="https://test.com",
            auth_username=SecretStr("user"),
            auth_password=SecretStr("pass")
        )

        credentials = TaskCredentials(username="testuser", password="testpass")
        task = LoginTask(url="https://test.com/login", credentials=credentials)

        mock_browser_context = Mock()

        with patch('browser_automation.agent_factory.ChatOpenAI'), \
             patch('browser_automation.agent_factory.Controller'), \
             patch('browser_automation.agent_factory.Agent') as mock_agent_class:

            mock_agent = Mock()
            mock_agent_class.return_value = mock_agent

            AgentFactory.create_agent(config, task, mock_browser_context)

            # Verify agent was created with task instructions
            call_kwargs = mock_agent_class.call_args.kwargs
            assert call_kwargs['task'] == task.get_instructions()
            assert "https://test.com/login" in call_kwargs['task']
            assert "testuser" in call_kwargs['task']

    def test_credentials_flow_from_config_to_task(self):
        """Test credentials flow from config to task creation."""
        username = "integration_user"
        password = "integration_pass"

        config = AppConfig(
            openai_api_key=SecretStr("sk-key"),
            chromium_path="/path/to/chromium",
            base_url="https://test.com",
            auth_username=SecretStr(username),
            auth_password=SecretStr(password)
        )

        # Validate config has credentials
        ConfigValidator.validate(config)
        assert config.auth_username is not None
        assert config.auth_username.get_secret_value() == username
        assert config.auth_password is not None
        assert config.auth_password.get_secret_value() == password

        # Create task with credentials from config
        credentials = TaskCredentials(
            username=config.auth_username.get_secret_value(),
            password=config.auth_password.get_secret_value()
        )
        task = LoginTask(url=config.base_url, credentials=credentials)

        # Verify credentials made it through
        assert task.credentials.username == username
        assert task.credentials.password == password


class TestAgentRunnerIntegration:
    """Test integration between agent creation and task execution."""

    @pytest.mark.asyncio
    async def test_agent_execution_through_runner(self):
        """Test agent execution through TaskRunner."""
        config = AppConfig(
            openai_api_key=SecretStr("sk-key"),
            chromium_path="/path/to/chromium",
            base_url="https://test.com",
            auth_username=SecretStr("user"),
            auth_password=SecretStr("pass")
        )

        credentials = TaskCredentials(username="user", password="pass")
        task = LoginTask(url=config.base_url, credentials=credentials)

        mock_browser_context = Mock()
        mock_browser_context.close = AsyncMock()

        with patch('browser_automation.agent_factory.ChatOpenAI'), \
             patch('browser_automation.agent_factory.Controller'), \
             patch('browser_automation.agent_factory.Agent') as mock_agent_class:

            mock_agent = Mock()
            mock_agent.run = AsyncMock(return_value="Login successful")
            mock_agent_class.return_value = mock_agent

            # Create agent
            agent = AgentFactory.create_agent(config, task, mock_browser_context)

            # Run agent through TaskRunner
            result = await TaskRunner.run(agent, mock_browser_context)

            # Verify execution
            assert result == "Login successful"
            mock_agent.run.assert_called_once()
            mock_browser_context.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_error_handling_through_runner(self):
        """Test error handling through the complete flow."""
        config = AppConfig(
            openai_api_key=SecretStr("sk-key"),
            chromium_path="/path/to/chromium",
            base_url="https://test.com",
            auth_username=SecretStr("user"),
            auth_password=SecretStr("pass")
        )

        credentials = TaskCredentials(username="user", password="pass")
        task = LoginTask(url=config.base_url, credentials=credentials)

        mock_browser_context = Mock()
        mock_browser_context.close = AsyncMock()

        with patch('browser_automation.agent_factory.ChatOpenAI'), \
             patch('browser_automation.agent_factory.Controller'), \
             patch('browser_automation.agent_factory.Agent') as mock_agent_class:

            mock_agent = Mock()
            mock_agent.run = AsyncMock(side_effect=RuntimeError("Login failed"))
            mock_agent_class.return_value = mock_agent

            agent = AgentFactory.create_agent(config, task, mock_browser_context)

            # Runner should propagate the error
            with pytest.raises(RuntimeError, match="Login failed"):
                await TaskRunner.run(agent, mock_browser_context)

            # Browser should still be closed
            mock_browser_context.close.assert_called_once()


class TestEndToEndWorkflow:
    """Test end-to-end workflow without actual browser/API calls."""

    @pytest.mark.asyncio
    async def test_complete_workflow_simulation(self):
        """Test complete workflow from config to task execution."""
        # Step 1: Load and validate config
        config = AppConfig(
            openai_api_key=SecretStr("sk-test-key"),
            chromium_path="/path/to/chromium",
            base_url="https://example.com/login",
            auth_username=SecretStr("admin"),
            auth_password=SecretStr("secure-pass")
        )

        ConfigValidator.validate(config)

        # Step 2: Create browser and context
        with patch('browser_automation.browser_factory.Browser') as mock_browser_class, \
             patch('browser_automation.browser_factory.BrowserContext') as mock_context_class, \
             patch('browser_automation.agent_factory.ChatOpenAI'), \
             patch('browser_automation.agent_factory.Controller'), \
             patch('browser_automation.agent_factory.Agent') as mock_agent_class:

            mock_browser = Mock()
            mock_browser_class.return_value = mock_browser
            mock_context = Mock()
            mock_context.close = AsyncMock()
            mock_context_class.return_value = mock_context

            browser = BrowserFactory.create_browser(config)
            browser_context = BrowserFactory.create_context(browser)

            # Step 3: Create task
            assert config.auth_username is not None
            assert config.auth_password is not None
            credentials = TaskCredentials(
                username=config.auth_username.get_secret_value(),
                password=config.auth_password.get_secret_value()
            )
            task = LoginTask(url=config.base_url, credentials=credentials)

            # Step 4: Create agent
            mock_agent = Mock()
            mock_agent.run = AsyncMock(return_value={
                "status": "success",
                "message": "Login completed"
            })
            mock_agent_class.return_value = mock_agent

            agent = AgentFactory.create_agent(config, task, browser_context)

            # Step 5: Run task
            result = await TaskRunner.run(agent, browser_context)

            # Verify complete workflow
            assert result["status"] == "success"
            assert browser is not None
            assert browser_context is not None
            assert agent is not None
            mock_browser_class.assert_called_once()
            mock_context_class.assert_called_once()
            mock_agent_class.assert_called_once()
            mock_agent.run.assert_called_once()
            mock_context.close.assert_called_once()

    def test_headless_mode_propagation(self):
        """Test that headless mode is properly propagated through the workflow."""
        # Create config with headless=True
        config = AppConfig(
            openai_api_key=SecretStr("sk-key"),
            chromium_path="/path/to/chromium",
            base_url="https://test.com",
            auth_username=SecretStr("user"),
            auth_password=SecretStr("pass"),
            headless=True
        )

        with patch('browser_automation.browser_factory.Browser') as mock_browser_class:
            mock_browser = Mock()
            mock_browser_class.return_value = mock_browser

            BrowserFactory.create_browser(config)

            # Verify headless was set in browser config
            call_kwargs = mock_browser_class.call_args.kwargs
            assert call_kwargs['config'].headless is True

    def test_model_propagation_to_llm(self):
        """Test that model selection is properly propagated to LLM."""
        custom_model = "gpt-4o"
        config = AppConfig(
            openai_api_key=SecretStr("sk-key"),
            chromium_path="/path/to/chromium",
            base_url="https://test.com",
            auth_username=SecretStr("user"),
            auth_password=SecretStr("pass"),
            model=custom_model
        )

        credentials = TaskCredentials(username="user", password="pass")
        task = LoginTask(url=config.base_url, credentials=credentials)
        mock_browser_context = Mock()

        with patch('browser_automation.agent_factory.ChatOpenAI') as mock_llm_class, \
             patch('browser_automation.agent_factory.Controller'), \
             patch('browser_automation.agent_factory.Agent'):

            AgentFactory.create_agent(config, task, mock_browser_context)

            # Verify model was passed to ChatOpenAI
            call_kwargs = mock_llm_class.call_args.kwargs
            assert call_kwargs['model'] == custom_model


class TestConfigurationOverrides:
    """Test configuration override scenarios."""

    def test_cli_overrides_simulate_flow(self):
        """Test simulating CLI overrides in the configuration flow."""
        # Simulate base config from environment
        base_config = AppConfig(
            openai_api_key=SecretStr("sk-key"),
            chromium_path="/path/to/chromium",
            base_url="https://default.com",
            auth_username=SecretStr("user"),
            auth_password=SecretStr("pass"),
            headless=False,
            model="gpt-4o-mini"
        )

        # Simulate CLI overrides (as done in task.py)
        base_config.headless = True
        base_config.base_url = "https://override.com"
        base_config.model = "gpt-4o"

        # Verify overrides took effect
        assert base_config.headless is True
        assert base_config.base_url == "https://override.com"
        assert base_config.model == "gpt-4o"

        # Verify validation still passes
        ConfigValidator.validate(base_config)
