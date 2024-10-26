"""Tests for Vault module"""

import unittest
from unittest.mock import Mock, patch
import structlog

from src.whispr.vault import SimpleVault


class SimpleVaultTest(unittest.TestCase):
    """Tests for Vault"""

    def setUp(self):
        # Mock logger and client to use in tests
        self.mock_logger = Mock(spec=structlog.BoundLogger)
        self.mock_client = Mock()

        # Subclass SimpleVault since it's abstract, only for testing
        class TestVault(SimpleVault):
            def fetch_secrets(self, secret_name: str) -> str:
                # Provide a simple implementation for the abstract method
                return "test_secret"

        self.vault = TestVault(logger=self.mock_logger, client=self.mock_client)

    @patch.object(
        SimpleVault, "__abstractmethods__", set()
    )  # This allows instantiation of SimpleVault directly if needed
    def test_initialization(self):
        """Test if the SimpleVault initializes with logger and client."""
        self.assertEqual(self.vault.logger, self.mock_logger)
        self.assertEqual(self.vault.client, self.mock_client)

    def test_fetch_secrets(self):
        """Test the fetch_secrets method to ensure it returns the expected result."""
        secret_name = "my_secret"
        result = self.vault.fetch_secrets(secret_name)
        self.assertEqual(result, "test_secret")
