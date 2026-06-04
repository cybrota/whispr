"""Bitwarden Secrets Manager"""

import structlog
from bitwarden_sdk import BitwardenClient

from whispr.vault import SimpleVault


class BitwardenVault(SimpleVault):
    """A Vault that maps secrets in Bitwarden Secrets Manager"""

    def __init__(self, logger: structlog.BoundLogger, client: BitwardenClient):
        """Initialize the Bitwarden Vault"""
        super().__init__(logger, client)

    def fetch_secrets(self, secret_name: str) -> str:
        """Fetch the secret from Bitwarden Secrets Manager."""
        try:
            secret = self.client.secrets().get(secret_name)
            self.logger.info(f"Successfully fetched bitwarden secret: {secret_name}")
            return secret.data.value
        except Exception as e:  # pragma: no cover - dependent on sdk exceptions
            self.logger.error("Error fetching secret", error=e)
            return ""
