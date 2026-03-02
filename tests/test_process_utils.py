import unittest
from unittest.mock import patch, MagicMock
import subprocess
import os

from whispr.utils.process import execute_command


class ProcessUtilsTestCase(unittest.TestCase):
    """Unit tests for the execute_command function, which executes commands with optional secrets."""

    def setUp(self):
        """Set up test data and mocks for logger and os environment."""
        self.command = ("echo Hello",)
        self.secrets = {"API_KEY": "123456"}
        self.no_env = True
        self.mock_logger = MagicMock()

    @patch("whispr.utils.process.logger", new_callable=lambda: MagicMock())
    @patch("subprocess.run")
    def test_execute_command_with_no_env(self, mock_subprocess_run, mock_logger):
        """Test execute_command with `no_env=True`, passing secrets as command arguments."""
        execute_command(self.command, self.no_env, self.secrets)

        expected_command = ["echo", "Hello", "API_KEY=123456"]
        mock_subprocess_run.assert_called_once_with(
            expected_command, env=os.environ, shell=False, check=True
        )

    @patch("whispr.utils.process.logger", new_callable=lambda: MagicMock())
    @patch("subprocess.run")
    def test_execute_command_with_env(
        self, mock_subprocess_run, mock_logger
    ):
        """Test execute_command with `no_env=False`, passing secrets via environment variables."""
        completed_process = subprocess.CompletedProcess(
            args=["echo", "Hello"], returncode=0, stdout=b"Hello\n", stderr=b""
        )
        mock_subprocess_run.return_value = completed_process

        original_api_key = os.environ.get("API_KEY")
        result = execute_command(self.command, no_env=False, secrets=self.secrets)
        if original_api_key is None:
            os.environ.pop("API_KEY", None)
        else:
            os.environ["API_KEY"] = original_api_key

        expected_command = ["echo", "Hello"]
        args, kwargs = mock_subprocess_run.call_args
        self.assertEqual(args[0], expected_command)
        self.assertEqual(kwargs["env"].get("API_KEY"), "123456")
        self.assertEqual(os.environ.get("API_KEY"), original_api_key)
        self.assertFalse(kwargs["shell"])
        self.assertTrue(kwargs["check"])

        self.assertIsInstance(result, subprocess.CompletedProcess)
        self.assertEqual(
            type(result.stdout), bytes
        )  # Additional sanity check on stdout type

    @patch("whispr.utils.process.logger", new_callable=lambda: MagicMock())
    @patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "test"))
    def test_execute_command_called_process_error(
        self, mock_subprocess_run, mock_logger
    ):
        """Test execute_command handles CalledProcessError and logs an error message."""
        with self.assertRaises(subprocess.CalledProcessError):
            execute_command(self.command, no_env=True, secrets=self.secrets)

        mock_logger.error.assert_called_once_with(
            f"Encountered a problem while running command: '{' '.join(self.command)}'. Aborting."
        )

    @patch("whispr.utils.process.logger", new_callable=lambda: MagicMock())
    @patch("subprocess.run")
    def test_execute_command_without_secrets(self, mock_subprocess_run, mock_logger):
        """Test execute_command without any secrets."""
        execute_command(self.command, no_env=True, secrets={})

        expected_command = ["echo", "Hello"]
        mock_subprocess_run.assert_called_once_with(
            expected_command,
            env=unittest.mock.ANY,
            shell=False,
            check=True,
        )
        mock_logger.error.assert_not_called()

    @patch("whispr.utils.process.logger", new_callable=lambda: MagicMock())
    @patch("subprocess.run")
    def test_execute_command_with_tuple_tokens(self, mock_subprocess_run, mock_logger):
        """Test execute_command accepts pre-tokenized command tuples."""
        command = ("python", "main.py", "--debug")
        execute_command(command, no_env=True, secrets={})

        mock_subprocess_run.assert_called_once_with(
            ["python", "main.py", "--debug"],
            env=unittest.mock.ANY,
            shell=False,
            check=True,
        )
        mock_logger.error.assert_not_called()
