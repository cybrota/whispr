import boto3
import structlog

from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from google.cloud import secretmanager

from whispr.vault import SimpleVault
from whispr.aws import AWSVault
from whispr.azure import AzureKeyVault
from whispr.gcp import GCPVault


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
            logger.info("Initializing vault", vault_type=vault_type)
            return AWSVault(logger, client)

        elif vault_type == "azure":
            vault_url = kwargs.get("vault_url")

            if not vault_url:
                raise ValueError(
                    f"Vault type: {vault_type} needs 'vault_url' set in whispr configuration."
                )

            client = SecretClient(vault_url=vault_url, credential=DefaultAzureCredential())
            logger.info("Initializing vault", vault_type=vault_type)
            return AzureKeyVault(logger, client)

        elif vault_type == "gcp":
            client = kwargs.get("client", secretmanager.SecretManagerServiceClient())
            logger.info("Initializing vault", vault_type=vault_type)
            return GCPVault(logger, client)

        else:
            raise ValueError(f"Unsupported vault type: {vault_type}")
