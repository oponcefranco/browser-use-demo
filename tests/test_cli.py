"""Tests for command-line argument parsing."""

import sys
from unittest.mock import patch
from cli import CLI


class TestCLIArguments:
    """Test command-line argument parsing."""

    def test_default_arguments(self):
        """Test default arguments (no CLI flags)."""
        with patch.object(sys, 'argv', ['task.py']):
            args = CLI.parse_arguments()
            assert args.headless is False
            assert args.url is None
            assert args.model is None

    def test_headless_flag(self):
        """Test --headless flag."""
        with patch.object(sys, 'argv', ['task.py', '--headless']):
            args = CLI.parse_arguments()
            assert args.headless is True
            assert args.url is None
            assert args.model is None

    def test_url_override(self):
        """Test --url flag."""
        test_url = 'https://example.com/login'
        with patch.object(sys, 'argv', ['task.py', '--url', test_url]):
            args = CLI.parse_arguments()
            assert args.headless is False
            assert args.url == test_url
            assert args.model is None

    def test_model_override(self):
        """Test --model flag."""
        test_model = 'gpt-4o'
        with patch.object(sys, 'argv', ['task.py', '--model', test_model]):
            args = CLI.parse_arguments()
            assert args.headless is False
            assert args.url is None
            assert args.model == test_model

    def test_combined_arguments(self):
        """Test multiple CLI flags together."""
        test_url = 'https://example.com/login'
        test_model = 'gpt-4o'
        with patch.object(sys, 'argv', ['task.py', '--headless', '--url', test_url, '--model', test_model]):
            args = CLI.parse_arguments()
            assert args.headless is True
            assert args.url == test_url
            assert args.model == test_model

    def test_help_exits(self):
        """Test that --help flag exits (argparse behavior)."""
        with patch.object(sys, 'argv', ['task.py', '--help']):
            try:
                CLI.parse_arguments()
                assert False, "Should have raised SystemExit"
            except SystemExit as e:
                # argparse exits with code 0 for --help
                assert e.code == 0
