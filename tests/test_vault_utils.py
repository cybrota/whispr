import unittest
from unittest.mock import patch, MagicMock
import json
from dotenv import dotenv_values

from whispr.utils.vault import fetch_secrets, get_filled_secrets, prepare_vault_config
from whispr.enums import VaultType


class SecretUtilsTestCase(unittest.TestCase):
    """Unit tests for the secret utilities: fetch_secrets, get_filled_secrets, and prepare_vault_config."""

    def setUp(self):
        """Set up test configuration and mock logger."""
        self.config = {
            "vault": VaultType.AWS.value,
            "secret_name": "test_secret",
        }
        self.vault_secrets = {"API_KEY": "123456"}
        self.env_file = ".env"
        self.mock_logger = MagicMock()

    @patch("whispr.utils.vault.logger", new_callable=lambda: MagicMock())
    @patch("whispr.utils.vault.VaultFactory.get_vault")
    def test_fetch_secrets_success(self, mock_get_vault, mock_logger):
        """Test fetch_secrets successfully retrieves and parses a secret."""
        mock_vault_instance = MagicMock()
        mock_vault_instance.fetch_secrets.return_value = json.dumps(self.vault_secrets)
        mock_get_vault.return_value = mock_vault_instance

        result = fetch_secrets(self.config)
        self.assertEqual(result, self.vault_secrets)

    @patch("whispr.utils.vault.logger", new_callable=lambda: MagicMock())
    def test_fetch_secrets_missing_config(self, mock_logger):
        """Test fetch_secrets logs an error if the vault type or secret name is missing."""
        config = {"vault": None, "secret_name": None}

        result = fetch_secrets(config)
        self.assertEqual(result, {})
        mock_logger.error.assert_called_once_with(
            "Vault type or secret name not specified in the configuration file."
        )

    @patch("whispr.utils.vault.logger", new_callable=lambda: MagicMock())
    @patch(
        "whispr.utils.vault.VaultFactory.get_vault",
        side_effect=ValueError("Invalid vault type"),
    )
    def test_fetch_secrets_invalid_vault(self, mock_get_vault, mock_logger):
        """Test fetch_secrets logs an error if the vault factory raises a ValueError."""
        result = fetch_secrets(
            {
                "vault": "UNKOWN",
                "secret_name": "test_secret",
            }
        )

        self.assertEqual(result, {})
        mock_logger.error.assert_called_once_with(
            "Error creating vault instance: Invalid vault type"
        )

    @patch(
        "whispr.utils.vault.dotenv_values",
        return_value={"API_KEY": "", "OTHER_KEY": ""},
    )
    @patch("whispr.utils.vault.logger", new_callable=lambda: MagicMock())
    def test_get_filled_secrets_partial_match(self, mock_logger, mock_dotenv_values):
        """Test get_filled_secrets fills only matching secrets from vault_secrets."""
        filled_secrets = get_filled_secrets(self.env_file, self.vault_secrets)

        self.assertEqual(filled_secrets, {"API_KEY": "123456"})
        mock_logger.warning.assert_called_once_with(
            "The given key: 'OTHER_KEY' is not found in vault. So ignoring it."
        )

    @patch("whispr.utils.vault.dotenv_values", return_value={"NON_MATCHING_KEY": ""})
    @patch("whispr.utils.vault.logger", new_callable=lambda: MagicMock())
    def test_get_filled_secrets_no_match(self, mock_logger, mock_dotenv_values):
        """Test get_filled_secrets returns an empty dictionary if no env variables match vault secrets."""
        filled_secrets = get_filled_secrets(self.env_file, self.vault_secrets)
        self.assertEqual(filled_secrets, {})
        mock_logger.warning.assert_called_once_with(
            "The given key: 'NON_MATCHING_KEY' is not found in vault. So ignoring it."
        )

    def test_prepare_vault_config_aws(self):
        """Test prepare_vault_config generates AWS configuration."""
        config = prepare_vault_config(VaultType.AWS.value)
        expected_config = {
            "env_file": ".env",
            "secret_name": "<your_secret_name>",
            "vault": VaultType.AWS.value,
        }
        self.assertEqual(config, expected_config)

    def test_prepare_vault_config_gcp(self):
        """Test prepare_vault_config generates GCP configuration."""
        config = prepare_vault_config(VaultType.GCP.value)
        expected_config = {
            "env_file": ".env",
            "secret_name": "<your_secret_name>",
            "vault": VaultType.GCP.value,
            "project_id": "<gcp_project_id>",
        }
        self.assertEqual(config, expected_config)

    def test_prepare_vault_config_azure(self):
        """Test prepare_vault_config generates Azure configuration."""
        config = prepare_vault_config(VaultType.AZURE.value)
        expected_config = {
            "env_file": ".env",
            "secret_name": "<your_secret_name>",
            "vault": VaultType.AZURE.value,
            "vault_url": "<azure_vault_url>",
        }
        self.assertEqual(config, expected_config)
