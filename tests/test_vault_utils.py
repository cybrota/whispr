import unittest
import string
from unittest.mock import patch, MagicMock
import json

from whispr.utils.vault import fetch_secrets, get_filled_secrets, prepare_vault_config
from whispr.utils.vault import get_raw_secret
from whispr.utils.crypto import generate_rand_secret
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

    def test_prepare_vault_config_aws_secrets_manager(self):
        """Test prepare_vault_config generates AWS configuration for secrets manager storage type."""
        config = prepare_vault_config(VaultType.AWS.value, vault_sub_type="secrets-manager")
        expected_config = {
            "env_file": ".env",
            "secret_name": "<your_secret_name>",
            "vault": {
                VaultType.AWS.value: {
                    "type": "secrets-manager",
                    "region": "<your_aws_default_region>"
                }
            },
        }
        self.assertEqual(config, expected_config)

    def test_prepare_vault_config_aws_parameter_store(self):
        """Test prepare_vault_config generates AWS configuration for parameter store storage type."""
        config = prepare_vault_config(VaultType.AWS.value, vault_sub_type="parameter-store")
        expected_config = {
            "env_file": ".env",
            "secret_name": "<your_secret_name>",
            "vault": {
                VaultType.AWS.value: {
                    "type": "parameter-store",
                    "region": "<your_aws_default_region>"
                }
            }
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


class CryptoUtilitiesTestCase(unittest.TestCase):
    """Unit tests for the crypto utilities: generate_rand_secret"""

    def test_basic_generation(self):
        """Test that a secret of the correct length is generated when no characters are excluded."""
        length = 12
        secret = generate_rand_secret(length, exclude_chars="")
        self.assertEqual(len(secret), length)
        # Check that all characters are from the default set
        all_chars = string.ascii_letters + string.digits + string.punctuation
        for ch in secret:
            self.assertIn(ch, all_chars)

    def test_exclusion_of_characters(self):
        """Test that specified characters are excluded from the generated secret."""
        length = 10
        exclude_chars = "ABCabc123"
        secret = generate_rand_secret(length, exclude_chars=exclude_chars)
        # Ensure excluded characters are not present in the secret
        for ch in exclude_chars:
            self.assertNotIn(ch, secret)

    def test_insufficient_characters(self):
        """Test that ValueError is raised if too many characters are excluded, making generation impossible."""
        length = 5
        # Exclude almost everything except 4 characters
        # For instance, exclude all uppercase letters, digits, punctuation
        # plus 22 of the 26 lowercase letters, leaving only 4 possible chars.
        # Then request length=5 => should raise ValueError.
        exclude_chars = (
            string.ascii_uppercase
            + string.digits
            + string.punctuation
            + "abcdefghijklmnopqrstuvwxyz"[4:]
        )
        with self.assertRaises(ValueError):
            generate_rand_secret(length, exclude_chars=exclude_chars)

    @patch("secrets.choice", return_value="X")
    def test_mocked_secrets_choice(self, mock_choice):
        """
        Test generate_rand_secret with secrets.choice mocked.
        This ensures we verify the function calls and final output deterministically.
        """
        length = 5
        secret = generate_rand_secret(length, exclude_chars="")
        # Since mock returns "X" every time, the result should be "XXXXX"
        self.assertEqual(secret, "XXXXX")

        # Verify that secrets.choice was called exactly 'length' times
        self.assertEqual(mock_choice.call_count, length)

    def test_zero_length(self):
        """
        Test generating a secret of zero length (uncommon, but functionally should return an empty string).
        """
        secret = generate_rand_secret(0, exclude_chars="")
        self.assertEqual(secret, "", "Zero-length secret should be an empty string.")

    def test_all_punctuation_exclusion(self):
        """
        Test excluding all punctuation does not break the generation.
        """
        length = 8
        exclude_chars = string.punctuation
        secret = generate_rand_secret(length, exclude_chars=exclude_chars)
        self.assertEqual(len(secret), length)
        # Ensure no punctuation is in the result
        for ch in secret:
            self.assertNotIn(ch, string.punctuation)


class GetRawSecretTestCase(unittest.TestCase):
    """Unit tests for get_raw_secret function."""

    def setUp(self):
        """Set up shared test data."""
        self.secret_name = "test_secret"
        self.aws_region = "us-east-1"
        self.azure_vault_url = "https://my-azure-vault.vault.azure.net/"
        self.gcp_project_id = "my-gcp-project"

    @patch("whispr.utils.vault.logger", new_callable=MagicMock)
    @patch("whispr.utils.vault.fetch_secrets")
    def test_no_vault_provided(self, mock_fetch_secrets, mock_logger):
        """Test that an empty dict is returned and an error is logged when no vault is provided."""
        mock_fetch_secrets.return_value = {"some_key": "some_value"}

        result = get_raw_secret(self.secret_name, vault="")

        # Expect an empty dict, an error log, and no call to fetch_secrets
        self.assertEqual(result, {})
        mock_logger.error.assert_called_once()
        mock_fetch_secrets.assert_not_called()

    @patch("whispr.utils.vault.logger", new_callable=MagicMock)
    @patch("whispr.utils.vault.fetch_secrets")
    def test_no_secret_name_provided(self, mock_fetch_secrets, mock_logger):
        """Test that an empty dict is returned and an error is logged when no secret name is provided."""
        mock_fetch_secrets.return_value = {"some_key": "some_value"}

        result = get_raw_secret(secret_name="", vault=VaultType.AWS.value, region=self.aws_region)

        self.assertEqual(result, {})
        mock_logger.error.assert_called_once()
        mock_fetch_secrets.assert_not_called()

    @patch("whispr.utils.vault.logger", new_callable=MagicMock)
    @patch("whispr.utils.vault.fetch_secrets")
    def test_aws_missing_region(self, mock_fetch_secrets, mock_logger):
        """Test that an empty dict is returned and an error is logged for AWS if region is missing."""
        mock_fetch_secrets.return_value = {"aws_key": "aws_value"}

        result = get_raw_secret(self.secret_name, VaultType.AWS.value)

        self.assertEqual(result, {})
        mock_logger.error.assert_called_once()
        mock_fetch_secrets.assert_not_called()

    @patch("whispr.utils.vault.logger", new_callable=MagicMock)
    @patch("whispr.utils.vault.fetch_secrets")
    def test_azure_missing_vault_url(self, mock_fetch_secrets, mock_logger):
        """Test that an empty dict is returned and an error is logged for Azure if vault_url is missing."""
        mock_fetch_secrets.return_value = {"azure_key": "azure_value"}

        result = get_raw_secret(self.secret_name, VaultType.AZURE.value)

        self.assertEqual(result, {})
        mock_logger.error.assert_called_once()
        mock_fetch_secrets.assert_not_called()

    @patch("whispr.utils.vault.logger", new_callable=MagicMock)
    @patch("whispr.utils.vault.fetch_secrets")
    def test_gcp_missing_project_id(self, mock_fetch_secrets, mock_logger):
        """Test that an empty dict is returned and an error is logged for GCP if project_id is missing."""
        mock_fetch_secrets.return_value = {"gcp_key": "gcp_value"}

        result = get_raw_secret(self.secret_name, VaultType.GCP.value)

        self.assertEqual(result, {})
        mock_logger.error.assert_called_once()
        mock_fetch_secrets.assert_not_called()

    @patch("whispr.utils.vault.logger", new_callable=MagicMock)
    @patch("whispr.utils.vault.fetch_secrets")
    def test_aws_success(self, mock_fetch_secrets, mock_logger):
        """Test successful retrieval for AWS with valid region."""
        expected_response = {"aws_key": "aws_value"}
        mock_fetch_secrets.return_value = expected_response

        result = get_raw_secret(
            secret_name=self.secret_name,
            vault=VaultType.AWS.value,
            region=self.aws_region
        )

        self.assertEqual(result, expected_response)
        mock_logger.error.assert_not_called()
        mock_fetch_secrets.assert_called_once_with({
            "secret_name": self.secret_name,
            "vault": VaultType.AWS.value,
            "region": self.aws_region
        })

    @patch("whispr.utils.vault.logger", new_callable=MagicMock)
    @patch("whispr.utils.vault.fetch_secrets")
    def test_azure_success(self, mock_fetch_secrets, mock_logger):
        """Test successful retrieval for Azure with valid vault_url."""
        expected_response = {"azure_key": "azure_value"}
        mock_fetch_secrets.return_value = expected_response

        result = get_raw_secret(
            secret_name=self.secret_name,
            vault=VaultType.AZURE.value,
            vault_url=self.azure_vault_url
        )

        self.assertEqual(result, expected_response)
        mock_logger.error.assert_not_called()
        mock_fetch_secrets.assert_called_once_with({
            "secret_name": self.secret_name,
            "vault": VaultType.AZURE.value,
            "vault_url": self.azure_vault_url
        })

    @patch("whispr.utils.vault.logger", new_callable=MagicMock)
    @patch("whispr.utils.vault.fetch_secrets")
    def test_gcp_success(self, mock_fetch_secrets, mock_logger):
        """Test successful retrieval for GCP with valid project_id."""
        expected_response = {"gcp_key": "gcp_value"}
        mock_fetch_secrets.return_value = expected_response

        result = get_raw_secret(
            secret_name=self.secret_name,
            vault=VaultType.GCP.value,
            project_id=self.gcp_project_id
        )

        self.assertEqual(result, expected_response)
        mock_logger.error.assert_not_called()
        mock_fetch_secrets.assert_called_once_with({
            "secret_name": self.secret_name,
            "vault": VaultType.GCP.value,
            "project_id": self.gcp_project_id
        })
