# browser-use-demo

AI-powered browser automation demo using the [browser-use](https://github.com/browser-use/browser-use) framework and OpenAI's GPT-4.

## Overview

This project demonstrates how to use AI agents to automate browser tasks. The demo performs an automated login flow on a test website using natural language instructions interpreted by GPT-4.

## Features

- 🤖 **AI-Driven Automation**: Uses GPT-4 to intelligently navigate and interact with web pages
- 🔐 **Secure Credential Management**: Environment variable-based configuration with SecretStr protection
- 🎯 **Smart Element Detection**: AI identifies form fields and buttons without explicit selectors
- 📝 **Comprehensive Logging**: Detailed logging for debugging and monitoring
- ⚙️ **Configurable**: Easy customization via environment variables
- 🧩 **Modular Architecture**: Clean separation of concerns with dedicated modules for config, browser, agent, and tasks
- ✅ **Fully Tested**: Comprehensive test suite with unit and integration tests

## Prerequisites

- Python 3.13+ (specified in `.python-version`)
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- Pipenv for dependency management

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd browser-use-demo
   ```

2. **Install dependencies:**
   ```bash
   pipenv install
   ```

3. **Install browser (required for automation):**
   ```bash
   pipenv run patchright install chromium
   ```
   > **Note:** This project uses [patchright](https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python) (an undetected fork of Playwright) for browser automation.

## Configuration

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your settings:**
   ```bash
   # Required: Your OpenAI API key
   OPENAI_API_KEY=sk-your-api-key-here

   # Required: Target website URL
   BASE_URL=https://practicetestautomation.com/practice-test-login/

   # Required: Login credentials
   AUTH_USERNAME=student
   AUTH_PASSWORD=Password123

   # Optional: Custom Chromium path (leave empty to use auto-installed browser)
   CHROMIUM_PATH=

   # Optional: Telemetry setting
   ANONYMIZED_TELEMETRY=true

   # Optional: Logging level (result | debug | info)
   BROWSER_USE_LOGGING_LEVEL=info
   ```

### Configuration Options

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `OPENAI_API_KEY` | Yes | Your OpenAI API key | - |
| `BASE_URL` | Yes | Target website URL | - |
| `AUTH_USERNAME` | Yes | Login username | - |
| `AUTH_PASSWORD` | Yes | Login password | - |
| `CHROMIUM_PATH` | No | Custom browser path (leave empty for auto-installed) | Empty (auto) |
| `ANONYMIZED_TELEMETRY` | No | Enable telemetry | `true` |
| `BROWSER_USE_LOGGING_LEVEL` | No | Logging verbosity | `info` |

## Usage

Run the automation task:

```bash
pipenv run python task.py
```

### Command-Line Options

```bash
python task.py [OPTIONS]

Options:
  --headless          Run browser in headless mode (no visible window)
  --url URL           Override BASE_URL from environment variables
  --model MODEL       Override OpenAI model (default: gpt-4o-mini)
  -h, --help          Show help message and exit

Examples:
  python task.py                              # Run with .env settings
  python task.py --headless                   # Run in headless mode
  python task.py --url https://example.com    # Override URL
  python task.py --headless --model gpt-4o    # Combine options
```

### What It Does

The script will:
1. Navigate to the configured URL
2. Locate the login form using AI
3. Enter the username and password
4. Submit the form
5. Verify successful login by checking for success message and logout button

### Example Output

```
2025-01-05 10:30:00 - __main__ - INFO - Starting browser automation task...
2025-01-05 10:30:00 - __main__ - INFO - Configuration validated successfully
2025-01-05 10:30:01 - __main__ - INFO - Initializing agent with model: gpt-4o-mini
2025-01-05 10:30:01 - __main__ - INFO - Configuring browser (headless=False)
2025-01-05 10:30:02 - __main__ - INFO - Starting agent navigation task...
2025-01-05 10:30:15 - __main__ - INFO - Navigation task completed successfully!
2025-01-05 10:30:15 - __main__ - INFO - Task completed successfully!
```

## Project Structure

```
browser-use-demo/
├── browser_automation/           # Main package (modular design)
│   ├── __init__.py              # Package exports
│   ├── config.py                # Configuration management
│   ├── agent_factory.py         # AI agent creation
│   ├── browser_factory.py       # Browser initialization
│   ├── runner.py                # Task execution orchestration
│   └── tasks/                   # Task implementations
│       ├── __init__.py
│       ├── base.py              # Base task interface
│       └── login_task.py        # Login automation task
├── task.py                      # Main entry point
├── cli.py                       # Command-line interface
├── tests/                       # Comprehensive test suite
│   ├── test_config.py           # Config validation (156 tests)
│   ├── test_cli.py              # CLI parsing (6 tests)
│   ├── test_agent_factory.py   # Agent factory (320 tests)
│   ├── test_browser_factory.py # Browser factory (198 tests)
│   ├── test_runner.py           # Task runner (259 tests)
│   ├── test_tasks.py            # Task implementations (321 tests)
│   └── test_integration.py     # End-to-end (354 tests)
├── .env                         # Environment configuration
├── .env.example                 # Environment template
├── Pipfile                      # Python dependencies
└── conftest.py                  # Pytest configuration
```

## How It Works

The application uses a modular architecture with clear separation of concerns:

1. **Config Module** (`config.py`): Validates and manages environment variables
2. **Browser Factory** (`browser_factory.py`): Initializes Chromium with proper configuration
3. **Agent Factory** (`agent_factory.py`): Creates AI agent with GPT-4 model and task instructions
4. **Task System** (`tasks/`): Defines task interface and implementations (e.g., login flow)
5. **Runner** (`runner.py`): Orchestrates task execution and handles cleanup

**Execution Flow:**
1. CLI parses arguments → Config loads/validates environment
2. Runner initializes browser and agent factories
3. Task executes: navigate → interact → validate
4. Results logged and browser cleanup

## Security Notes

⚠️ **Important Security Considerations:**

- **Never commit `.env` file** to version control (already in `.gitignore`)
- **Rotate API keys regularly** for security
- **Use test credentials only** for demo purposes
- **Don't hardcode secrets** in source code
- **Review `.gitignore`** before committing

## Troubleshooting

### Missing Configuration Error
```
Configuration errors:
  - OPENAI_API_KEY environment variable is required
```
**Solution**: Ensure all required variables are set in `.env` file

### Browser Not Found
```
Error: Executable doesn't exist at /Users/.../ms-playwright/chromium-XXXX/...
```
**Solution**: Install the browser with:
```bash
pipenv run patchright install chromium
```
Leave `CHROMIUM_PATH` empty in `.env` to use the auto-installed browser.

### API Rate Limits
```
Error: Rate limit exceeded
```
**Solution**: Wait and retry, or upgrade your OpenAI plan

## Customization

### Using a Different Model

Use CLI argument or modify config:
```bash
# Via CLI
python task.py --model gpt-4o

# Or set default in browser_automation/config.py
```

### Headless Mode

```bash
python task.py --headless
```

### Custom Tasks

Create new task classes in `browser_automation/tasks/`:
```python
from browser_automation.tasks.base import BaseTask

class MyTask(BaseTask):
    async def execute(self, agent):
        # Your automation logic
        pass
```

## Development

### Running Tests

Comprehensive test suite covering unit, integration, and end-to-end scenarios.

```bash
# Install dev dependencies
pipenv install --dev

# Run all tests
pipenv run pytest

# Run with coverage report
pipenv run pytest --cov=browser_automation --cov=cli --cov=task

# Run specific test modules
pipenv run pytest tests/test_config.py -v
pipenv run pytest tests/test_integration.py -v
```

**Test Coverage:**
- **Config validation**: Environment variables, SecretStr protection, validation logic
- **Agent factory**: Model initialization, instruction building, configuration
- **Browser factory**: Chromium setup, headless mode, custom paths
- **Task runner**: Execution flow, error handling, cleanup
- **Task implementations**: Login flow, base task interface
- **Integration tests**: End-to-end automation scenarios
- **CLI parsing**: Argument validation and overrides

All modules fully tested with mocks for external dependencies (OpenAI, Playwright).

### Code Style
Modular architecture following SOLID principles with type hints throughout.

## Resources

- [browser-use Documentation](https://docs.browser-use.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Patchright Documentation](https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python)
- [Playwright Documentation](https://playwright.dev/python/)


For issues and questions:
- Review OpenAI API status

---

**Note**: This is a demonstration project for learning purposes. For production use, implement additional error handling, monitoring, and security measures.

## License

MIT License - see [LICENSE](LICENSE) file for details