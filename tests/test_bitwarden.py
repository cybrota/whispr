"""Tests for Bitwarden module"""

import unittest
from unittest.mock import MagicMock

from whispr.bitwarden import BitwardenVault


class BitwardenVaultTestCase(unittest.TestCase):
    """Unit tests for BitwardenVault class."""

    def setUp(self):
        self.mock_logger = MagicMock()
        self.mock_client = MagicMock()
        self.mock_secrets_client = MagicMock()
        self.mock_client.secrets.return_value = self.mock_secrets_client
        self.vault = BitwardenVault(logger=self.mock_logger, client=self.mock_client)

    def test_initialization(self):
        self.assertEqual(self.vault.logger, self.mock_logger)
        self.assertEqual(self.vault.client, self.mock_client)

    def test_fetch_secrets_success(self):
        mock_secret = MagicMock()
        mock_secret.data.value = '{"key": "value"}'
        self.mock_secrets_client.get.return_value = mock_secret

        result = self.vault.fetch_secrets("test_secret")
        self.assertEqual(result, '{"key": "value"}')
        self.mock_secrets_client.get.assert_called_with("test_secret")

    def test_fetch_secrets_exception(self):
        self.mock_secrets_client.get.side_effect = Exception("error")

        result = self.vault.fetch_secrets("bad_secret")
        self.assertEqual(result, "")
        self.mock_logger.error.assert_called()
