import os
import unittest
from unittest.mock import MagicMock, patch

import botocore.exceptions

from whispr.aws import AWSVault
from whispr.azure import AzureVault
from whispr.gcp import GCPVault

from whispr.factory import VaultFactory


class FactoryTestCase(unittest.TestCase):
    """Unit tests for Factory method to create vaults"""

    def setUp(self):
        """Set up mocks for logger, GCP client, and project_id before each test."""
        self.mock_logger = MagicMock()
        os.environ["AWS_DEFAULT_REGION"] = "us-west-2"

    def test_get_aws_vault_simple_client(self):
        """Test AWSVault client without SSO"""
        config = {
            "vault": "aws",
            "env": ".env",
            "secret_name": "dummy_secret",
            "logger": self.mock_logger,
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
        }

        mock_session.side_effect = botocore.exceptions.ProfileNotFound(profile="dev")
        with self.assertRaises(ValueError):
            VaultFactory.get_vault(**config)

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

    def test_get_gcp_vault_client(self):
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
