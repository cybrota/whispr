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
    def get_vault(vault_type: str, logger: structlog.BoundLogger, **kwargs) -> SimpleVault:
        """
        Factory method to return the appropriate secret manager based on the vault type.

        :param vault_type: The type of the vault ('aws', 'azure', 'gcp').
        :param logger: Structlog logger instance.
        :param kwargs: Any additional parameters required for specific vault clients.
        :return: An instance of a concrete Secret manager class.
        """
        if vault_type == 'aws':
            client = kwargs.get('client', boto3.client('secretsmanager'))
            logger.info("Creating AWS Vault", vault_type=vault_type)
            return AWSVault(logger, client)

        elif vault_type == 'azure':
            client = kwargs.get('client', SecretClient(
                vault_url=kwargs.get('vault_url'),
                credential=DefaultAzureCredential()
            ))
            logger.info("Creating Azure Key Vault", vault_type=vault_type)
            return AzureKeyVault(logger, client)

        elif vault_type == 'gcp':
            client = kwargs.get('client', secretmanager.SecretManagerServiceClient())
            logger.info("Creating GCP Vault", vault_type=vault_type)
            return GCPVault(logger, client)

        else:
            logger.error("Unsupported vault type", vault_type=vault_type)
            raise ValueError(f"Unsupported vault type: {vault_type}")
