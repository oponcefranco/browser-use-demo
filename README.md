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
├── task.py              # Main application file
├── tests/               # Unit tests
│   ├── __init__.py      # Test package initialization
│   ├── test_config.py   # Configuration validation tests
│   └── test_cli.py      # CLI argument parsing tests
├── .env                 # Environment configuration (create from .env.example)
├── .env.example         # Template for environment variables
├── Pipfile              # Python dependencies
├── Pipfile.lock         # Locked dependency versions
├── conftest.py          # Pytest configuration
├── cookie.txt           # Cookie template (optional)
├── .gitignore           # Git ignore patterns
├── .python-version      # Python version specification
├── LICENSE              # MIT License
└── README.md            # This file
```

## How It Works

1. **Configuration Loading**: Environment variables are loaded and validated
2. **Agent Initialization**: GPT-4 model is configured with task instructions
3. **Browser Setup**: Chromium browser is launched with specified configuration
4. **Task Execution**: AI agent interprets natural language instructions and performs actions:
   - Navigates to URL
   - Identifies form elements
   - Enters credentials
   - Submits form
   - Validates results
5. **Cleanup**: Browser is closed and results are logged

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

Edit `.env` or modify `task.py`:
```python
config = AppConfig(
    model="gpt-4o",  # Use GPT-4 instead of gpt-4o-mini
    # ... other config
)
```

### Headless Mode

For running without visible browser:
```python
config = AppConfig(
    headless=True,  # Run in headless mode
    # ... other config
)
```

### Custom Task Instructions

Modify the task string in `task.py` `create_agent()` function to automate different workflows.

## Development

### Running Tests

The project includes comprehensive unit tests for configuration validation and CLI argument parsing.

```bash
# Install dev dependencies
pipenv install --dev

# Run all tests
pipenv run pytest

# Run tests with verbose output
pipenv run pytest -v

# Run specific test file
pipenv run pytest tests/test_config.py -v

# Run with coverage
pipenv run pytest --cov=task
```

**Test Coverage:**
- Configuration validation (14 test cases)
- CLI argument parsing (6 test cases)
- All tests passing ✅

### Code Style
This project follows PEP 8 guidelines and uses type hints throughout for better code clarity and IDE support.

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