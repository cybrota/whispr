"""Tests for Azure module"""

import unittest
from unittest.mock import Mock, MagicMock, ANY

import structlog
from azure.core.exceptions import ResourceNotFoundError

from whispr.vault import SimpleVault
from whispr.azure import AzureVault


class AzureVaultTestCase(unittest.TestCase):
    """Unit tests for AzureVault class, which fetches secrets from Azure Key Vault."""

    def setUp(self):
        """Set up mocks for logger, Azure client, and vault URL before each test."""
        self.mock_logger = MagicMock()
        self.mock_client = MagicMock()
        self.vault_url = "https://example-vault.vault.azure.net/"
        self.vault = AzureVault(
            logger=self.mock_logger, client=self.mock_client, vault_url=self.vault_url
        )

    def test_initialization(self):
        """Test that AzureVault initializes with logger, client, and vault_url correctly."""
        self.assertEqual(self.vault.logger, self.mock_logger)
        self.assertEqual(self.vault.client, self.mock_client)
        self.assertEqual(self.vault.vault_url, self.vault_url)

    def test_fetch_secrets_success(self):
        """Test successful fetch of secrets from Azure Key Vault."""
        # Mock the client response
        mock_secret = MagicMock()
        mock_secret.value = '{"key": "value"}'
        self.mock_client.get_secret.return_value = mock_secret

        result = self.vault.fetch_secrets("test_secret")
        self.assertEqual(result, '{"key": "value"}')
        self.mock_logger.info.assert_any_call("Successfully fetched secret: test_secret")
        self.mock_logger.info.assert_any_call(
            "Secret fetched",
            secret_name="test_secret",
            vault_type="azure",
            fetched_at=ANY,
        )
        self.mock_client.get_secret.assert_called_with("test_secret")

    def test_fetch_secrets_resource_not_found(self):
        """Test fetch_secrets handles ResourceNotFoundError gracefully."""
        # Set up the client to raise ResourceNotFoundError
        self.mock_client.get_secret.side_effect = ResourceNotFoundError(
            "Secret not found"
        )

        result = self.vault.fetch_secrets("non_existent_secret")
        self.assertEqual(result, "")
        self.mock_logger.error.assert_called_with(
            "The given secret: non_existent_secret is not found on azure vault. Please check the secret name, vault name or subscription ID."
        )

    def test_fetch_secrets_generic_exception(self):
        """Test fetch_secrets raises exception and logs an error for generic exceptions."""
        # Set up the client to raise a generic exception
        exception_message = "Some generic error"
        self.mock_client.get_secret.side_effect = Exception(exception_message)

        with self.assertRaises(Exception) as context:
            self.vault.fetch_secrets("generic_error_secret")
        self.assertEqual(str(context.exception), exception_message)

        # Extract the actual call to the logger and check its arguments
        self.assertTrue(self.mock_logger.error.called)
        error_call = self.mock_logger.error.call_args
        self.assertEqual(
            error_call[0][0],
            f"Error fetching secret: generic_error_secret, Error: {exception_message}",
        )
