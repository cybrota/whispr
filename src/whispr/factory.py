"""Vault factory"""

import boto3
import botocore.exceptions
import structlog
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from google.cloud import secretmanager

from whispr.aws import AWSVault
from whispr.azure import AzureVault
from whispr.gcp import GCPVault
from whispr.vault import SimpleVault
from whispr.enums import VaultType


class VaultFactory:
    """A factory class to create client objects"""

    @staticmethod
    def get_vault(**kwargs) -> SimpleVault:
        """
        Factory method to return the appropriate secrets manager client based on the vault type.

        :param vault_type: The type of the vault ('aws', 'azure', 'gcp').
        :param logger: Structlog logger instance.
        :param kwargs: Any additional parameters required for specific vault clients.
        :return: An instance of a concrete Secret manager class.
        """
        vault_type = kwargs.get("vault")
        sso_profile = kwargs.get("sso_profile")
        logger: structlog.BoundLogger = kwargs.get("logger")
        logger.info("Initializing vault", vault_type=vault_type)

        if vault_type == VaultType.AWS.value:
            client = boto3.client("secretsmanager")

            # When SSO profile is supplied use the session client
            if sso_profile:
                try:
                    session = boto3.Session(profile_name=sso_profile)
                    client = session.client("secretsmanager")
                except botocore.exceptions.ProfileNotFound:
                    raise ValueError(
                        f"The config profile {sso_profile} could not be found for vault: `{vault_type}`. Please check your AWS SSO config file and retry."
                    )
            return AWSVault(logger, client)

        elif vault_type == VaultType.AZURE.value:
            vault_url = kwargs.get("vault_url")
            if not vault_url:
                raise ValueError(
                    f"Vault type: {vault_type} needs a 'vault_url' set in 'whispr.yaml' file"
                )

            client = SecretClient(
                vault_url=vault_url, credential=DefaultAzureCredential()
            )
            return AzureVault(logger, client, vault_url)

        elif vault_type == VaultType.GCP.value:
            project_id = kwargs.get("project_id")
            if not project_id:
                raise ValueError(
                    f"Project ID is not supplied for vault: {vault_type}. \
                    Please set the 'project_id' key in whispr.yaml config file to continue."
                )
            client = secretmanager.SecretManagerServiceClient()

            return GCPVault(logger, client, project_id)
        # TODO: Add HashiCorp Vault implementation
        else:
            raise ValueError(f"Unsupported vault type: {vault_type}")
