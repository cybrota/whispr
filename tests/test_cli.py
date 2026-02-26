# Copyright (c) 2025 Naren Yellavula & Cybrota contributors
# Apache License, Version 2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""Tests for CLI commands."""

import unittest
from unittest.mock import patch

from click.testing import CliRunner

from whispr import cli as cli_module


class CLITestCase(unittest.TestCase):
    """Unit tests for the whispr click CLI."""

    def setUp(self):
        self.runner = CliRunner()

    @patch("whispr.cli.logger")
    @patch("whispr.cli.write_to_yaml_file")
    @patch("whispr.cli.prepare_vault_config", return_value={"vault": "aws"})
    def test_init_command_writes_config(self, mock_prepare, mock_write, mock_logger):
        result = self.runner.invoke(cli_module.cli, ["init", "aws", "parameter-store"])

        self.assertEqual(result.exit_code, 0)
        mock_prepare.assert_called_once_with("aws", "parameter-store")
        mock_write.assert_called_once_with({"vault": "aws"}, cli_module.CONFIG_FILE)
        mock_logger.info.assert_called_once_with("config file created at: %s")

    @patch("whispr.cli.logger")
    @patch("whispr.cli.os.path.exists", return_value=False)
    def test_run_errors_when_config_missing(self, _mock_exists, mock_logger):
        result = self.runner.invoke(cli_module.cli, ["run", "python app.py"])

        self.assertEqual(result.exit_code, 0)
        mock_logger.error.assert_called_once_with(
            "whispr configuration file not found. Run 'whispr init' first."
        )

    @patch("whispr.cli.logger")
    @patch("whispr.cli.os.path.exists", return_value=True)
    def test_run_errors_when_no_command_given(self, _mock_exists, mock_logger):
        result = self.runner.invoke(cli_module.cli, ["run"])

        self.assertEqual(result.exit_code, 0)
        mock_logger.error.assert_called_once()

    @patch("whispr.cli.logger")
    @patch("whispr.cli.load_config", return_value={})
    @patch("whispr.cli.os.path.exists", return_value=True)
    def test_run_errors_when_env_file_not_in_config(
        self, _mock_exists, _mock_load_config, mock_logger
    ):
        result = self.runner.invoke(cli_module.cli, ["run", "python app.py"])

        self.assertEqual(result.exit_code, 0)
        mock_logger.error.assert_called_once_with(
            "'env_file' is not set in the whispr config"
        )

    @patch("whispr.cli.logger")
    @patch("whispr.cli.load_config", return_value={"env_file": ".env"})
    @patch(
        "whispr.cli.os.path.exists",
        side_effect=lambda path: path == cli_module.CONFIG_FILE,
    )
    def test_run_errors_when_env_file_missing(
        self, _mock_exists, _mock_load_config, mock_logger
    ):
        result = self.runner.invoke(cli_module.cli, ["run", "python app.py"])

        self.assertEqual(result.exit_code, 0)
        mock_logger.error.assert_called_once_with(
            "Environment variables file: '.env' defined in whispr config doesn't exist"
        )

    @patch("whispr.cli.execute_command")
    @patch("whispr.cli.get_filled_secrets")
    @patch("whispr.cli.fetch_secrets", return_value={})
    @patch("whispr.cli.load_config", return_value={"env_file": ".env"})
    @patch("whispr.cli.os.path.exists", return_value=True)
    def test_run_returns_when_vault_secret_fetch_fails(
        self,
        _mock_exists,
        _mock_load_config,
        _mock_fetch,
        mock_get_filled,
        mock_execute,
    ):
        result = self.runner.invoke(cli_module.cli, ["run", "python app.py"])

        self.assertEqual(result.exit_code, 0)
        mock_get_filled.assert_not_called()
        mock_execute.assert_not_called()

    @patch("whispr.cli.execute_command")
    @patch("whispr.cli.get_filled_secrets", return_value={"API_KEY": "123"})
    @patch("whispr.cli.fetch_secrets", return_value={"API_KEY": "123"})
    @patch("whispr.cli.load_config", return_value={"env_file": ".env", "no_env": True})
    @patch("whispr.cli.os.path.exists", return_value=True)
    def test_run_executes_command_with_filled_secrets(
        self,
        _mock_exists,
        _mock_load_config,
        _mock_fetch,
        mock_get_filled,
        mock_execute,
    ):
        result = self.runner.invoke(cli_module.cli, ["run", "python app.py"])

        self.assertEqual(result.exit_code, 0)
        mock_get_filled.assert_called_once_with(".env", {"API_KEY": "123"})
        mock_execute.assert_called_once_with(
            ("python app.py",), no_env=True, secrets={"API_KEY": "123"}
        )

    @patch("whispr.cli.get_raw_secret", return_value={})
    def test_secret_get_with_empty_response_prints_nothing(self, mock_get_raw_secret):
        result = self.runner.invoke(
            cli_module.cli,
            [
                "secret",
                "get",
                "--secret-name",
                "my-secret",
                "--vault",
                "aws",
                "--region",
                "us-east-1",
            ],
        )

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, "")
        mock_get_raw_secret.assert_called_once()

    @patch("whispr.cli.get_raw_secret", return_value={"TOKEN": "abc"})
    def test_secret_get_prints_json(self, _mock_get_raw_secret):
        result = self.runner.invoke(
            cli_module.cli,
            [
                "secret",
                "get",
                "--secret-name",
                "my-secret",
                "--vault",
                "aws",
                "--region",
                "us-east-1",
            ],
        )

        self.assertEqual(result.exit_code, 0)
        self.assertIn('"TOKEN": "abc"', result.output)

    @patch("whispr.cli.generate_rand_secret", return_value="generated-secret")
    def test_secret_gen_random_uses_defaults(self, mock_generate):
        result = self.runner.invoke(cli_module.cli, ["secret", "gen-random"])

        self.assertEqual(result.exit_code, 0)
        mock_generate.assert_called_once_with(length=16, exclude_chars="")
        self.assertEqual(result.output.strip(), "generated-secret")

    @patch("whispr.cli.generate_rand_secret", return_value="filtered-secret")
    def test_secret_gen_random_uses_passed_options(self, mock_generate):
        result = self.runner.invoke(
            cli_module.cli,
            ["secret", "gen-random", "--length", "20", "--exclude", "abc123"],
        )

        self.assertEqual(result.exit_code, 0)
        mock_generate.assert_called_once_with(length=20, exclude_chars="abc123")
        self.assertEqual(result.output.strip(), "filtered-secret")
