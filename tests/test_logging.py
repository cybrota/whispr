# Copyright (c) 2025 Naren Yellavula & Cybrota contributors
# Apache License, Version 2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""Tests for logging helpers."""

import unittest
from pathlib import Path, PosixPath
from unittest.mock import ANY, MagicMock, patch

from whispr import logging as logging_module


class LoggingHelpersTestCase(unittest.TestCase):
    """Unit tests for path resolution and log helper functions."""

    @patch("whispr.logging.os.getenv", return_value="/tmp/custom_whispr.log")
    def test_default_log_path_uses_env_override(self, _mock_getenv):
        result = logging_module._default_log_path()
        self.assertEqual(result, "/tmp/custom_whispr.log")

    @patch("whispr.logging.os.getenv", side_effect=lambda key: None)
    @patch("whispr.logging.os.name", "posix")
    def test_default_log_path_on_posix(self, _mock_getenv):
        result = logging_module._default_log_path()
        self.assertEqual(result, "/var/log/whispr/access.log")

    @patch("whispr.logging.os.name", "nt")
    @patch("whispr.logging.Path", PosixPath)
    @patch(
        "whispr.logging.os.getenv",
        side_effect=lambda key: {"WHISPR_LOG_PATH": None, "PROGRAMDATA": "C:/ProgramData"}.get(
            key
        ),
    )
    def test_default_log_path_on_windows(self, _mock_getenv):
        result = logging_module._default_log_path()
        self.assertEqual(result, "C:/ProgramData/whispr/access.log")

    @patch("whispr.logging._default_log_path", return_value="/tmp/primary.log")
    @patch("whispr.logging._ensure_writable_log_path", return_value=True)
    def test_resolve_log_path_uses_primary_when_writable(
        self, mock_ensure_writable, _mock_default
    ):
        result = logging_module._resolve_log_path()
        self.assertEqual(result, "/tmp/primary.log")
        mock_ensure_writable.assert_called_once_with("/tmp/primary.log")

    @patch("whispr.logging._default_log_path", return_value="/tmp/primary.log")
    @patch("whispr.logging._ensure_writable_log_path", side_effect=[False, True])
    @patch("whispr.logging.platform.system", return_value="Darwin")
    @patch("whispr.logging.Path.home", return_value=Path("/Users/tester"))
    def test_resolve_log_path_uses_darwin_fallback(
        self, _mock_home, _mock_system, _mock_ensure_writable, _mock_default
    ):
        result = logging_module._resolve_log_path()
        self.assertEqual(result, "/Users/tester/Library/Logs/whispr/access.log")

    @patch("whispr.logging._default_log_path", return_value="/tmp/primary.log")
    @patch("whispr.logging._ensure_writable_log_path", side_effect=[False, False])
    @patch("whispr.logging.platform.system", return_value="Linux")
    @patch("whispr.logging.Path.home", return_value=Path("/home/tester"))
    @patch("whispr.logging.Path.cwd", return_value=Path("/workspace"))
    def test_resolve_log_path_uses_cwd_as_last_resort(
        self,
        _mock_cwd,
        _mock_home,
        _mock_system,
        _mock_ensure_writable,
        _mock_default,
    ):
        result = logging_module._resolve_log_path()
        self.assertEqual(result, "/workspace/whispr_access.log")

    @patch("whispr.logging.Path.open", side_effect=OSError("permission denied"))
    @patch("whispr.logging.Path.mkdir")
    def test_ensure_writable_log_path_returns_false_on_oserror(
        self, _mock_mkdir, _mock_open
    ):
        self.assertFalse(logging_module._ensure_writable_log_path("/tmp/access.log"))

    def test_log_secret_fetch_adds_expected_fields(self):
        logger_instance = MagicMock()

        logging_module.log_secret_fetch(logger_instance, "test-secret", "aws")

        logger_instance.info.assert_called_once_with(
            "Secret fetched",
            secret_name="test-secret",
            vault_type="aws",
            fetched_at=ANY,
        )
