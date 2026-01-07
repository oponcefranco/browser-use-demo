"""Command-line interface for browser automation."""
import argparse


class CLI:
    """Command-line interface handler."""

    @staticmethod
    def parse_arguments() -> argparse.Namespace:
        """Parse command-line arguments.

        Returns:
            Parsed command-line arguments
        """
        parser = argparse.ArgumentParser(
            description='AI-powered browser automation demo using browser-use framework',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python task.py                          # Run with default settings from .env
  python task.py --headless               # Run in headless mode
  python task.py --url https://example.com  # Override BASE_URL
  python task.py --headless --url https://example.com  # Combine options

Environment Variables:
  See .env.example for all available configuration options.
            """
        )
        parser.add_argument(
            '--headless',
            action='store_true',
            help='Run browser in headless mode (no visible window)'
        )
        parser.add_argument(
            '--url',
            type=str,
            help='Override BASE_URL from environment variables'
        )
        parser.add_argument(
            '--model',
            type=str,
            help='Override OpenAI model (default: gpt-4o-mini)'
        )
        return parser.parse_args()
