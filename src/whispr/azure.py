"""Azure Key Vault"""

import json

from azure.keyvault.secrets import SecretClient
import structlog

from whispr.vault import SimpleVault


class AzureKeyVault(SimpleVault):
    """A Vault that maps secrets in Azure Key Vault"""

    def __init__(self, logger: structlog.BoundLogger, client: SecretClient):
        """
        Initialize the Azure Vault.

        :param logger: Logger instance.
        :param client: Azure Key Vault client.
        """
        super().__init__(logger, client)

    def fetch_secret(self, secret_name: str) -> str:
        """
        Fetch the secret from Azure Key Vault.

        :param secret_name: The name of the secret.
        :return: Secret value as a Key/Value JSON string.
        """
        try:
            secret = self.client.get_secret(secret_name)
            self.logger.info(f"Successfully fetched secret: {secret_name}")
            return json.dumps({"value": secret.value})
        except Exception as e:
            self.logger.error(f"Error fetching secret: {secret_name}, Error: {e}")
            raise
