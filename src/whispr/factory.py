"""Vault factory"""

import boto3
import structlog
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from google.cloud import secretmanager

from whispr.aws import AWSVault
from whispr.azure import AzureKeyVault
from whispr.gcp import GCPVault
from whispr.vault import SimpleVault


class VaultFactory:
    @staticmethod
    def get_vault(
        vault_type: str, logger: structlog.BoundLogger, **kwargs
    ) -> SimpleVault:
        """
        Factory method to return the appropriate secret manager based on the vault type.

        :param vault_type: The type of the vault ('aws', 'azure', 'gcp').
        :param logger: Structlog logger instance.
        :param kwargs: Any additional parameters required for specific vault clients.
        :return: An instance of a concrete Secret manager class.
        """
        if vault_type == "aws":
            client = boto3.client("secretsmanager")
            logger.info(f"Initializing {vault_type} vault")
            return AWSVault(logger, client)

        elif vault_type == "azure":
            vault_url = kwargs.get("vault_url")

            if not vault_url:
                raise ValueError(
                    f"Vault type: {vault_type} needs 'vault_url' set in whispr configuration."
                )

            client = SecretClient(
                vault_url=vault_url, credential=DefaultAzureCredential()
            )
            logger.info(f"Initializing {vault_type} vault")
            return AzureKeyVault(logger, client)

        elif vault_type == "gcp":
            client = kwargs.get("client", secretmanager.SecretManagerServiceClient())
            logger.info(f"Initializing {vault_type} vault")
            return GCPVault(logger, client)

        else:
            raise ValueError(f"Unsupported vault type: {vault_type}")
