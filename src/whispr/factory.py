"""Vault factory"""

import os

import boto3
import botocore.exceptions
import structlog
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from google.cloud import secretmanager

from whispr.aws import AWSVault, AWSSSMVault
from whispr.azure import AzureVault
from whispr.gcp import GCPVault
from whispr.bitwarden import BitwardenVault
from bitwarden_sdk import BitwardenClient, DeviceType, client_settings_from_dict
from whispr.vault import SimpleVault
from whispr.enums import VaultType, AWSVaultSubType


class VaultFactory:
    """A factory class to create client objects"""

    @staticmethod
    def get_aws_region(kwargs: dict) -> str:
        """
        Retrieves the AWS region from the provided kwargs or environment variable.

        :param kwargs: Any additional parameters required for specific vault clients.

        Order of preference:
          1. 'region' key in kwargs
          2. AWS_DEFAULT_REGION environment variable

        Raises:
            ValueError: If neither source provides a region."""

        region = kwargs.get("region")

        if not region:
            region = os.environ.get("AWS_DEFAULT_REGION")

        if not region:
            raise ValueError(
                "AWS Region not found. Please fill the `region` (Ex: us-west-2) in Whispr config or set AWS_DEFAULT_REGION environment variable."
            )

        return region

    @staticmethod
    def _get_aws_client(region: str, sub_type: str) -> boto3.client:
        """Builds a AWS client based on sub type"""
        if sub_type == AWSVaultSubType.SECRETS_MANAGER.value:
            return boto3.client("secretsmanager", region_name=region)
        elif sub_type == AWSVaultSubType.PARAMETER_STORE.value:
            return boto3.client("ssm", region_name=region)

    @staticmethod
    def _get_aws_sso_client(
        region: str, sso_profile_name: str, sub_type: str
    ) -> boto3.client:
        """Builds a AWS client based on sub type and SSO profile"""
        session = boto3.Session(profile_name=sso_profile_name)
        if sub_type == AWSVaultSubType.SECRETS_MANAGER.value:
            return session.client("secretsmanager", region_name=region)
        elif sub_type == AWSVaultSubType.PARAMETER_STORE.value:
            return session.client("ssm", region_name=region)

    @staticmethod
    def get_vault(**kwargs) -> SimpleVault:
        """
        Factory method to return the appropriate secrets manager client based on the vault type.

        :param vault_type: The type of the vault ('aws', 'azure', 'gcp').
        :param logger: Structlog logger instance.
        :param kwargs: Any additional parameters required for specific vault clients.
        :return: An instance of a concrete Secret manager class.

        Raises:
            ValueError: If sufficient information is not avaiable to initialize vault instance.
        """
        vault_type = kwargs.get("vault")
        logger: structlog.BoundLogger = kwargs.get("logger")
        logger.debug("Initializing vault", vault_type=vault_type)

        if vault_type == VaultType.AWS.value:
            vault_sub_type: str | None = None

            if kwargs.get("type"):
                vault_sub_type = kwargs.get("type")
            else:
                # Fall back to secrets manager if type is not available
                vault_sub_type = AWSVaultSubType.SECRETS_MANAGER.value

            region = VaultFactory.get_aws_region(kwargs)
            client = VaultFactory._get_aws_client(
                region=region, sub_type=vault_sub_type
            )

            sso_profile = kwargs.get("sso_profile")
            # When SSO profile is supplied, use the session client
            if sso_profile:
                try:
                    client = VaultFactory._get_aws_sso_client(
                        region=region,
                        sso_profile_name=sso_profile,
                        sub_type=vault_sub_type,
                    )
                except botocore.exceptions.ProfileNotFound:
                    raise ValueError(
                        f"The config profile {sso_profile} could not be found for vault: `{vault_type}`. Please check your AWS SSO config file and retry."
                    )

            if vault_sub_type == AWSVaultSubType.SECRETS_MANAGER.value:
                return AWSVault(logger, client)
            else:
                return AWSSSMVault(logger, client)

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
        elif vault_type == VaultType.BITWARDEN.value:
            access_token = kwargs.get("access_token")
            if not access_token:
                raise ValueError(
                    f"Access token is not supplied for vault: {vault_type}. "
                    "Please set the 'access_token' key in whispr.yaml config file to continue."
                )
            state_file = kwargs.get("state_file")
            api_url = kwargs.get("api_url", "https://api.bitwarden.com")
            identity_url = kwargs.get("identity_url", "https://identity.bitwarden.com")
            settings = client_settings_from_dict({"apiUrl": api_url, "deviceType": DeviceType.SDK, "identityUrl": identity_url, "userAgent": "Whispr"})
            client = BitwardenClient(settings)
            client.auth().login_access_token(access_token, state_file)
            return BitwardenVault(logger, client)
        # TODO: Add HashiCorp Vault implementation
        else:
            raise ValueError(f"Unsupported vault type: {vault_type}")
