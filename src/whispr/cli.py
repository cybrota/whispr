"""whispr CLI entrypoint"""

import os

import click

from whispr.logging import logger
from whispr.utils.io import (
    load_config,
    write_to_yaml_file,
)
from whispr.utils.process import execute_command

from whispr.utils.vault import (
    fetch_secrets,
    get_filled_secrets,
    prepare_vault_config
)

CONFIG_FILE = "whispr.yaml"


@click.group()
def cli():
    """Click group"""
    pass


@click.command()
@click.argument("vault", nargs=1, type=click.STRING)
def init(vault):
    """Creates a whispr configuration file"""
    config = prepare_vault_config(vault)
    write_to_yaml_file(config, CONFIG_FILE)


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

    no_env = config.get("no_env", False)
    execute_command(command, no_env=no_env, secrets=filled_env_vars)


cli.add_command(init)
cli.add_command(run)

if __name__ == "__main__":
    cli()
