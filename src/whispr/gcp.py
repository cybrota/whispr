import logging
import json

from google.cloud import secretmanager
from whispr.vault import SimpleVault

class GCPVault(SimpleVault):
    def __init__(self, logger: logging.Logger, client: secretmanager.SecretManagerServiceClient):
        """
        Initialize the GCP Vault.

        :param logger: Logger instance.
        :param client: GCP Secret Manager client.
        """
        super().__init__(logger, client)

    def fetch_secret(self, secret_name: str) -> str:
        """
        Fetch the secret from GCP Secret Manager.

        :param secret_name: The name of the secret.
        :return: Secret value as a Key/Value JSON string.
        """
        try:
            secret_name = f"projects/my-project/secrets/{secret_name}/versions/latest"
            response = self.client.access_secret_version(name=secret_name)
            secret_data = response.payload.data.decode('UTF-8')
            self.logger.info(f"Successfully fetched secret: {secret_name}")
            return json.dumps({"value": secret_data})
        except Exception as e:
            self.logger.error(f"Error fetching secret: {secret_name}, Error: {e}")
            raise
