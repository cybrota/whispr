import json

from dotenv import dotenv_values

from whispr.factory import VaultFactory
from whispr.logging import logger
from whispr.enums import VaultType, AWSVaultSubType


def fetch_secrets(config: dict) -> dict:
    """Fetch secret from relevant vault"""
    kwargs = config
    kwargs["logger"] = logger

    vault = config.get("vault")
    secret_name = config.get("secret_name")

    if not vault:
        logger.error(
            "Vault is not specified in the configuration file. Set `vault` key."
        )
        return {}

    if not secret_name:
        logger.error(
            "Secret name is not specified in the configuration file. Set `secret_name` key."
        )
        return {}

    try:
        vault_instance = VaultFactory.get_vault(**kwargs)
    except ValueError as e:
        logger.error(f"Error creating vault instance: {str(e)}")
        return {}

    secret_string = vault_instance.fetch_secrets(secret_name)
    if not secret_string:
        return {}

    return json.loads(secret_string)


def get_filled_secrets(env_file: str, vault_secrets: dict) -> dict:
    """Inject vault secret values into local empty secrets"""

    filled_secrets = {}
    env_vars = dotenv_values(dotenv_path=env_file)

    # Iterate over .env variables and check if they exist in the fetched secrets
    for key in env_vars:
        if key in vault_secrets:
            filled_secrets[key] = vault_secrets[key]  # Collect the matching secrets
        else:
            logger.warning(
                f"The given key: '{key}' is not found in vault. So ignoring it."
            )

    return filled_secrets


def prepare_vault_config(vault_type: str, vault_sub_type: str = "") -> dict:
    """Prepares in-memory configuration for a given vault"""
    config = {"secret_name": "<your_secret_name>", "env_file": ".env"}

    # Add more configuration fields as needed for other secret managers.
    if vault_type == VaultType.GCP.value:
        config["project_id"] = "<gcp_project_id>"
        config["vault"] = VaultType.GCP.value
    elif vault_type == VaultType.AZURE.value:
        config["vault_url"] = "<azure_vault_url>"
        config["vault"] = VaultType.AZURE.value
    elif vault_type == VaultType.AWS.value:
        config["vault"] = VaultType.AWS.value
        if vault_sub_type == AWSVaultSubType.SECRETS_MANAGER.value:
            config["type"] = AWSVaultSubType.SECRETS_MANAGER.value
        elif vault_sub_type == AWSVaultSubType.PARAMETER_STORE.value:
            config["type"] = AWSVaultSubType.PARAMETER_STORE.value

    return config


def get_raw_secret(secret_name: str, vault: str, **kwargs) -> dict:
    """Get raw secret from the vault"""

    if not vault:
        logger.error(
            "No vault type is provided to get-secret sub command. Use --vault=aws/azure/gcp as value."
        )
        return {}

    if not secret_name:
        logger.error(
            "No secret name is provided to get-secret sub command. Use --secret_name=<val> option."
        )
        return {}

    # Parse kwargs
    region = kwargs.get("region")
    vault_url = kwargs.get("vault_url")
    project_id = kwargs.get("project_id")
    config = {}

    if vault == VaultType.AWS.value:
        if not region:
            logger.error(
                "No region option provided to get-secret sub command for AWS Vault. Use --region=<val> option."
            )
            return {}

        config = {"secret_name": secret_name, "vault": vault, "region": region}
    elif vault == VaultType.AZURE.value:
        if not vault_url:
            logger.error(
                "No Azure vault URL option is provided to get-secret sub command.  Use --vault-url=<val> option."
            )
            return {}

        config = {
            "secret_name": secret_name,
            "vault": vault,
            "vault_url": vault_url,
        }
    elif vault == VaultType.GCP.value:
        if not project_id:
            logger.error(
                "No project ID option is provided to get-secret sub command for GCP Vault. Use --project-id=<val> option."
            )
            return {}

        config = {
            "secret_name": secret_name,
            "vault": vault,
            "project_id": project_id,
        }

    # Fetch secret based on the vault type
    vault_secrets = fetch_secrets(config)

    return vault_secrets
