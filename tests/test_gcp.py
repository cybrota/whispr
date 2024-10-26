"""Tests for GCP module"""

import unittest
from unittest.mock import Mock, patch, MagicMock

import google.api_core.exceptions
import structlog

from whispr.vault import SimpleVault
from whispr.gcp import GCPVault


class GCPVaultTestCase(unittest.TestCase):
    """Unit tests for GCPVault class, which fetches secrets from GCP Secrets Manager."""

    def setUp(self):
        """Set up mocks for logger, GCP client, and project_id before each test."""
        self.mock_logger = MagicMock()
        self.mock_client = MagicMock()
        self.project_id = "test_project_id"
        self.vault = GCPVault(
            logger=self.mock_logger, client=self.mock_client, project_id=self.project_id
        )

    def test_initialization(self):
        """Test that GCPVault initializes with logger, client, and project_id correctly."""
        self.assertEqual(self.vault.logger, self.mock_logger)
        self.assertEqual(self.vault.client, self.mock_client)
        self.assertEqual(self.vault.project_id, self.project_id)

    def test_fetch_secrets_success(self):
        """Test successful fetch of secrets from GCP Secrets Manager."""
        # Mock the client response
        mock_response = MagicMock()
        mock_response.payload.data.decode.return_value = '{"key": "value"}'
        self.mock_client.access_secret_version.return_value = mock_response

        result = self.vault.fetch_secrets("test_secret")
        self.assertEqual(result, '{"key": "value"}')
        self.mock_logger.info.assert_called_with(
            "Successfully fetched gcp secret: projects/test_project_id/secrets/test_secret/versions/latest"
        )
        self.mock_client.access_secret_version.assert_called_with(
            name="projects/test_project_id/secrets/test_secret/versions/latest"
        )

    def test_fetch_secrets_not_found(self):
        """Test fetch_secrets handles NotFound exception gracefully."""
        # Set up the client to raise NotFound exception
        self.mock_client.access_secret_version.side_effect = (
            google.api_core.exceptions.NotFound("Secret not found")
        )

        result = self.vault.fetch_secrets("non_existent_secret")
        self.assertEqual(result, "")
        self.mock_logger.error.assert_called_with(
            "The given secret: projects/test_project_id/secrets/non_existent_secret/versions/latest is not found on gcp vault."
        )

    def test_fetch_secrets_generic_exception(self):
        """Test fetch_secrets handles generic exceptions gracefully."""
        # Set up the client to raise a generic exception
        exception_message = "Some generic error"
        self.mock_client.access_secret_version.side_effect = Exception(
            exception_message
        )

        result = self.vault.fetch_secrets("generic_error_secret")
        self.assertEqual(result, "")
        self.mock_logger.error.assert_called_with(
            f"Error encountered while fetching secret: projects/test_project_id/secrets/generic_error_secret/versions/latest, Error: {exception_message}"
        )
