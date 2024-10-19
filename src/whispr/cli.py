import json
import os
import subprocess

import click
import yaml
from dotenv import dotenv_values


from whispr.factory import VaultFactory
from whispr.logging import logger

CONFIG_FILE = 'whispr.yaml'

def _get_matched_secrets(env_file: str, vault_secrets: dict) -> dict:
    env_vars = dotenv_values(dotenv_path=env_file)  # This returns a dict of key-value pairs from .env
    print(env_file, env_vars)
    # Dictionary to collect variables from AWS secrets that match .env variables
    matched_secrets = {}

    # Iterate over .env variables and check if they exist in the fetched secrets
    for key in env_vars:
        if key in vault_secrets:
            matched_secrets[key] = vault_secrets[key]  # Collect the matching secrets
            os.environ[key] = vault_secrets[key]  # Update the current environment

    # Return the dictionary of matched secrets for further use if needed
    return matched_secrets

@click.group()
def cli():
    pass

@click.command()
def init():
    """Creates an empty configuration YAML file."""
    config = {
        'vault': 'aws',  # Options: aws, vault, 1password
        'secret_name': '<your_secret_name>',
        'env_file': '.env'
        # Add more configuration fields as needed for other secret managers.
    }

    if os.path.exists(CONFIG_FILE):
        click.echo(f"{CONFIG_FILE} already exists.")
    else:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as file:
            yaml.dump(config, file)
        click.echo(f"{CONFIG_FILE} has been created.")

@click.command()
@click.argument('command', nargs=-1, type=click.UNPROCESSED)
def run(command):
    """Fetches secrets and injects them into the environment."""
    if not os.path.exists(CONFIG_FILE):
        click.echo("Configuration file not found. Run 'whispr init' first.")
        return

    if not command:
        logger.error("No command provided to run.")

    # Load the configuration
    with open(CONFIG_FILE, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)

    vault = config['vault']
    secret_name = config['secret_name']
    env_file = config['env_file']

    # Fetch secret based on the vault type
    secret_value = None
    if vault == 'aws':
        aws_vault = VaultFactory.get_vault(
            vault_type='aws',
            logger=logger
        )
        secret_value = aws_vault.fetch_secret(secret_name)
    elif vault == 'azure':
        azure_vault = VaultFactory.get_vault(
            vault_type='azure',
            logger=logger,
            vault_url="https://myvault.vault.azure.net/"
        )
        secret_value = azure_vault.fetch_secret(secret_name)
    elif vault == 'gcp':
        gcp_vault = VaultFactory.get_vault(
            vault_type='gcp',
            logger=logger
        )
        secret_value = gcp_vault.fetch_secret(secret_name)
    else:
        logger.error(f"Unsupported vault type: {vault}")
        return

    secret_value = json.loads(secret_value)

    if secret_value:
        matched_env = _get_matched_secrets(env_file, secret_value)
        os.environ.update(matched_env)
        logger.info("Secrets have been successfully injected into the environment")

        try:
            # Remove capture_output=True to allow for interactive breakpoints
            subprocess.run(command, env=os.environ, shell=True, check=True)
        except FileNotFoundError:
            logger.error(f"Command not found: {command[0]}")
        except Exception as e:
            logger.error(f"An error occurred: {e}")

cli.add_command(init)
cli.add_command(run)

if __name__ == "__main__":
    cli()
