"""Azure Key Vault"""

import structlog
from azure.keyvault.secrets import SecretClient
import azure.core.exceptions
from whispr.vault import SimpleVault


class AzureVault(SimpleVault):
    """A Vault that maps secrets in Azure Key Vault"""

    def __init__(
        self, logger: structlog.BoundLogger, client: SecretClient, vault_url: str
    ):
        """
        Initialize the Azure Vault.

        :param logger: Logger instance.
        :param client: Azure Key Vault client.
        """
        super().__init__(logger, client)
        self.vault_url = vault_url

    def fetch_secrets(self, secret_name: str) -> str:
        """
        Fetch the secret from Azure Key Vault.

        :param secret_name: The name of the secret.
        :return: Secret value as a Key/Value JSON string.
        """
        try:
            secret = self.client.get_secret(secret_name)
            self.logger.info(f"Successfully fetched secret: {secret_name}")
            return secret.value
        except azure.core.exceptions.ResourceNotFoundError:
            self.logger.error(
                f"The given secret: {secret_name} is not found on azure vault. Please check the secret name, vault name or subscription ID."
            )
            return ""
        except Exception as e:
            self.logger.error(f"Error fetching secret: {secret_name}, Error: {e}")
            raise
