"""Abstract Class for Vault. A Vault is a secret store."""

from abc import ABC, abstractmethod
from typing import Any

import structlog


class SimpleVault(ABC):
    """A SimpleVault to abstract cloud secret vaults"""

    def __init__(self, logger: structlog.BoundLogger, client: Any):
        """
        Initialize the SimpleVault class with a logger and a client.

        :param logger: The logger instance to use for logging.
        :param client: The vault client instance (AWS, Azure, GCP, etc.).
        """
        self.logger = logger
        self.client = client

    @abstractmethod
    def fetch_secret(self, secret_name: str) -> str:
        """
        Abstract method to fetch the secret from the vault.

        :param secret_name: Name of the secret to fetch.
        :return: Secret as a JSON string.
        """
        pass
