"""GCP Secrets Manager"""

import structlog
from google.cloud import secretmanager
import google.api_core
from whispr.logging import log_secret_fetch
from whispr.vault import SimpleVault


class GCPVault(SimpleVault):
    """A Vault that maps secrets in GCP Secrets Manager"""

    def __init__(
        self,
        logger: structlog.BoundLogger,
        client: secretmanager.SecretManagerServiceClient,
        project_id: str,
    ):
        """
        Initialize the GCP Vault.

        :param logger: Logger instance.
        :param client: GCP Secret Manager client.
        """
        super().__init__(logger, client)
        self.project_id = project_id

    def fetch_secrets(self, secret_name: str) -> str:
        """
        Fetch the secret from GCP Secret Manager.

        :param secret_name: The name of the secret.
        :return: Secret value as a Key/Value JSON string.
        """
        try:
            secret_name = (
                f"projects/{self.project_id}/secrets/{secret_name}/versions/latest"
            )
            response = self.client.access_secret_version(name=secret_name)
            secret_data = response.payload.data.decode("UTF-8")
            self.logger.info(f"Successfully fetched gcp secret: {secret_name}")
            if secret_data:
                log_secret_fetch(self.logger, secret_name, "gcp")
            return secret_data
        except google.api_core.exceptions.NotFound:
            self.logger.error(
                f"The given secret: {secret_name} is not found on gcp vault."
            )
            return ""
        except Exception as e:
            self.logger.error(
                f"Error encountered while fetching secret: {secret_name}, Error: {e}"
            )
            return ""
