"""Tests for AWS module"""

import unittest
from unittest.mock import MagicMock, patch

import botocore.exceptions

from whispr.aws import AWSVault


class AWSVaultTestCase(unittest.TestCase):
    """Unit tests for AWSVault class, which fetches secrets from AWS Secrets Manager."""

    def setUp(self):
        """Set up mocks for logger and AWS client before each test."""
        self.mock_logger = MagicMock()
        self.mock_client = MagicMock()
        self.vault = AWSVault(logger=self.mock_logger, client=self.mock_client)

    def test_initialization(self):
        """Test that AWSVault initializes with logger and client correctly."""
        self.assertEqual(self.vault.logger, self.mock_logger)
        self.assertEqual(self.vault.client, self.mock_client)

    def test_fetch_secrets_success(self):
        """Test successful fetch of secrets from AWS Secrets Manager."""
        self.mock_client.get_secret_value.return_value = {
            "SecretString": '{"key": "value"}'
        }
        result = self.vault.fetch_secrets("test_secret")
        self.assertEqual(result, '{"key": "value"}')
        self.mock_client.get_secret_value.assert_called_with(SecretId="test_secret")

    def test_fetch_secrets_resource_not_found(self):
        """Test fetch_secrets handles ResourceNotFoundException gracefully."""
        # Set up the client to raise ResourceNotFoundException
        self.mock_client.get_secret_value.side_effect = botocore.exceptions.ClientError(
            {"Error": {"Code": "ResourceNotFoundException"}}, "get_secret_value"
        )

        result = self.vault.fetch_secrets("non_existent_secret")
        self.assertEqual(result, "")
        self.mock_logger.error.assert_called_with(
            "The secret is not found on AWS. Did you set the right AWS_DEFAULT_REGION ?",
            secret_name="non_existent_secret",
        )

    @patch("whispr.aws.AWSVault.fetch_secrets")
    def test_fetch_secrets_unrecognized_client_exception(self, mock_fetch_secrets):
        """Test fetch_secrets handles UnrecognizedClientException gracefully."""
        mock_fetch_secrets.side_effect = botocore.exceptions.ClientError(
            {"Error": {"Code": "UnrecognizedClientException"}}, "get_secret_value"
        )

        with self.assertRaises(botocore.exceptions.ClientError):
            result = self.vault.fetch_secrets("incorrect_credentials_secret")
            self.assertEqual(result, "")
            self.mock_logger.error.assert_called_with(
                "Incorrect AWS credentials set for operation. Please verify them and retry."
            )

    def test_fetch_secrets_generic_exception(self):
        """Test fetch_secrets raises exception and logs an error for generic exceptions."""
        # Set up the client to raise a generic exception
        exception_message = "Some generic error"
        self.mock_client.get_secret_value.side_effect = Exception(exception_message)

        with self.assertRaises(Exception) as context:
            self.vault.fetch_secrets("generic_error_secret")
        self.assertEqual(str(context.exception), exception_message)

        # Extract the actual call to the logger and check its arguments
        self.assertTrue(self.mock_logger.error.called)
        error_call = self.mock_logger.error.call_args
        self.assertEqual(error_call[0][0], "Error fetching secret")
        self.assertIsInstance(error_call[1]["error"], Exception)
        self.assertEqual(str(error_call[1]["error"]), exception_message)
