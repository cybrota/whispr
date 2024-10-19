"""Functions used by CLI"""

import json
import os
import shlex
import subprocess

import yaml
from dotenv import dotenv_values

from whispr.factory import VaultFactory
from whispr.logging import logger


def execute_command(command: tuple):
    """Executes a Unix/Windows command"""
    try:
        subprocess.run(shlex.split(command[0]), env=os.environ, shell=False, check=True)
    except subprocess.CalledProcessError:
        logger.error(
            f"Encountered a problem while running command: '{command[0]}'. Aborting."
        )


def fetch_secrets(config) -> dict:
    """Fetch secret from relevant vault"""

    vault = config.get("vault")
    secret_name = config.get("secret_name")
    if not vault or not secret_name:
        logger.error(
            "Vault type or secret name not specified in the configuration file."
        )
        return {}

    vault_instance = VaultFactory.get_vault(vault_type=vault, logger=logger)
    secret_string = vault_instance.fetch_secret(secret_name)
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
            os.environ[key] = vault_secrets[key]  # Update the current environment
        else:
            logger.warning(
                f"The given key: '{key}' is not found in vault. So ignoring it."
            )

    # Return the dictionary of matched secrets for further use if needed
    return filled_secrets


def load_config(config_file: str) -> dict:
    """Loads a given config file"""
    try:
        with open(config_file, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)
    except Exception as e:
        raise e
