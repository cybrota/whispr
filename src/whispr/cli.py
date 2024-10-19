"""whispr CLI entrypoint"""

import os

import click
import yaml

from whispr.logging import logger
from whispr.utils import execute_command, fetch_secrets, get_filled_secrets, load_config

CONFIG_FILE = "whispr.yaml"


@click.group()
def cli():
    """Click group"""
    pass


@click.command()
def init():
    """Creates a whispr configuration file"""

    config = {
        "env_file": ".env",
        "secret_name": "<your_secret_name>",
        "vault": "aws",  # Options: aws, vault, 1password
        # Add more configuration fields as needed for other secret managers.
    }

    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as file:
            yaml.dump(config, file)
        logger.info(f"{CONFIG_FILE} has been created.")


@click.command()
@click.argument("command", nargs=-1, type=click.UNPROCESSED)
def run(command):
    """Fetches secrets and injects them into the environment."""
    if not os.path.exists(CONFIG_FILE):
        logger.error("whispr configuration file not found. Run 'whispr init' first.")
        return

    if not command:
        logger.error(
            "No command provided to whispr. Use: whispr run '<your_command' \
            (please mind quotes) to inject secrets and run subcommand"
        )
        return

    config = load_config(CONFIG_FILE)

    env_file = config.get("env_file")
    if not env_file:
        logger.error("'env_file' is not set in the whispr config")
        return

    if not os.path.exists(env_file):
        logger.error(
            f"Environment variables file: '{env_file}' defined in whispr config doesn't exist"
        )
        return

    # Fetch secret based on the vault type
    vault_secrets = fetch_secrets(config)
    if not vault_secrets:
        return

    filled_env_vars = get_filled_secrets(env_file, vault_secrets)
    os.environ.update(filled_env_vars)
    logger.info("Secrets have been successfully injected into the environment")

    execute_command(command)


cli.add_command(init)
cli.add_command(run)

if __name__ == "__main__":
    cli()
