import unittest
from unittest.mock import MagicMock, patch

import botocore.exceptions

from whispr.aws import AWSVault
from whispr.azure import AzureVault
from whispr.gcp import GCPVault

from whispr.factory import VaultFactory

from .utils import patch_env_var


class FactoryTestCase(unittest.TestCase):
    """Unit tests for Factory method to create vaults"""

    def setUp(self):
        """Set up mocks for logger, GCP client, and project_id before each test."""
        self.mock_logger = MagicMock()

    def test_get_aws_vault_simple_client(self):
        """Test AWSVault client without SSO"""
        config = {
            "vault": "aws",
            "env": ".env",
            "secret_name": "dummy_secret",
            "logger": self.mock_logger,
            "region": "us-east-2",
        }
        vault_instance = VaultFactory.get_vault(**config)
        self.assertIsInstance(vault_instance, AWSVault)

    @patch("boto3.Session")
    def test_get_aws_vault_sso_client(self, mock_session):
        """Test AWSVault SSO session client"""
        config = {
            "vault": "aws",
            "env": ".env",
            "secret_name": "dummy_secret",
            "sso_profile": "dev",
            "logger": self.mock_logger,
            "region": "us-east-2",
        }
        vault_instance = VaultFactory.get_vault(**config)
        self.assertIsInstance(vault_instance, AWSVault)
        mock_session.assert_called_with(profile_name="dev")

    @patch("boto3.Session")
    def test_get_aws_vault_sso_client_profile_not_found(self, mock_session):
        """Test AWSVault raises exception when sso_profile is defined but not found in AWS config"""
        config = {
            "vault": "aws",
            "env": ".env",
            "secret_name": "dummy_secret",
            "sso_profile": "dev",
            "logger": self.mock_logger,
            "region": "us-east-1",
        }

        mock_session.side_effect = botocore.exceptions.ProfileNotFound(profile="dev")
        with self.assertRaises(ValueError):
            VaultFactory.get_vault(**config)

    @patch("boto3.client")
    def test_get_aws_vault_region_passed_explicitly(self, mock_boto_client):
        """Test AWSVault client with region passed explicitly in config"""
        config = {
            "vault": "aws",
            "env": ".env",
            "secret_name": "dummy_secret",
            "region": "us-west-2",  # Explicit region
            "logger": self.mock_logger,
        }
        print(VaultFactory.get_vault(**config).client)
        mock_boto_client.assert_called_with("secretsmanager", region_name="us-west-2")

    @patch("boto3.client")
    @patch_env_var("AWS_DEFAULT_REGION", "us-east-1")
    def test_get_aws_vault_region_from_env_variable(self, mock_boto_client):
        """Test AWSVault client with region from AWS_DEFAULT_REGION environment variable"""
        config = {
            "vault": "aws",
            "env": ".env",
            "secret_name": "dummy_secret",
            "logger": self.mock_logger,
        }
        VaultFactory.get_vault(**config)
        mock_boto_client.assert_called()
        mock_boto_client.assert_called_with("secretsmanager", region_name="us-east-1")

    @patch("boto3.client")
    def test_get_aws_vault_region_not_passed_nor_in_env_raises_error(
        self, mock_boto_client
    ):
        """Test AWSVault raises error when region is neither passed nor in AWS_DEFAULT_REGION environment variable"""
        config = {
            "vault": "aws",
            "env": ".env",
            "secret_name": "dummy_secret",
            "logger": self.mock_logger,
        }
        with self.assertRaises(ValueError):
            VaultFactory.get_vault(**config)
        mock_boto_client.assert_not_called()  # Client should not be called if error is raised

    @patch("boto3.client")
    @patch_env_var("AWS_DEFAULT_REGION", "us-east-1")  # Set env variable
    def test_get_aws_vault_region_passed_takes_precedence_over_env_variable(
        self, mock_boto_client
    ):
        """Test AWSVault client with region passed explicitly takes precedence over AWS_DEFAULT_REGION environment variable"""
        config = {
            "vault": "aws",
            "env": ".env",
            "secret_name": "dummy_secret",
            "region": "us-west-2",  # Explicit region
            "logger": self.mock_logger,
        }
        VaultFactory.get_vault(**config)
        mock_boto_client.assert_called_with("secretsmanager", region_name="us-west-2")

    def test_get_azure_vault_client(self):
        """Test AzureVault client"""
        config = {
            "vault": "azure",
            "env": ".env",
            "secret_name": "dummy_secret",
            "vault_url": "https://example.org",
            "logger": self.mock_logger,
        }
        vault_instance = VaultFactory.get_vault(**config)
        self.assertIsInstance(vault_instance, AzureVault)

    def test_get_azure_vault_client_no_url(self):
        """Test AzureVault raises exception when vault_url is not defined in config"""
        config = {
            "vault": "azure",
            "env": ".env",
            "secret_name": "dummy_secret",
            "logger": self.mock_logger,
        }

        with self.assertRaises(ValueError):
            VaultFactory.get_vault(**config)

    @patch("google.cloud.secretmanager.SecretManagerServiceClient")
    def test_get_gcp_vault_client(self, mock_client):
        """Test GCPVault client"""
        config = {
            "vault": "gcp",
            "env": ".env",
            "secret_name": "dummy_secret",
            "project_id": "dummy_project",
            "logger": self.mock_logger,
        }
        vault_instance = VaultFactory.get_vault(**config)
        self.assertIsInstance(vault_instance, GCPVault)
        mock_client.assert_called_once()

    def test_get_gcp_vault_client_no_project_id(self):
        """Test GCPVault raises exception when project_id is not defined in config"""
        config = {
            "vault": "gcp",
            "env": ".env",
            "secret_name": "dummy_secret",
            "logger": self.mock_logger,
        }

        with self.assertRaises(ValueError):
            VaultFactory.get_vault(**config)
