"""whispr CLI entrypoint"""

import os
import json

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
    prepare_vault_config,
    get_raw_secret,
)

from whispr.utils.crypto import generate_rand_secret

CONFIG_FILE = "whispr.yaml"
MIN_GENERATION_LENGTH = 16


@click.group()
def cli():
    """Whispr is a CLI tool to safely inject vault secrets into an application.
    Run `whispr init <vault>` to create a configuration.

    Availble values for <vault>: ["aws", "azure", "gcp"]
    """
    pass


@click.command()
@click.argument("vault", nargs=1, type=click.STRING)
def init(vault):
    """Creates a whispr vault configuration file (YAML). This file defines vault properties like secret name and vault type etc."""
    config = prepare_vault_config(vault)
    write_to_yaml_file(config, CONFIG_FILE)


@click.command()
@click.argument("command", nargs=-1, type=click.UNPROCESSED)
def run(command):
    """Runs a command by injecting secrets fetched from vault via environment or list of command arguments. Make sure you run `whispr init` command before using this.
    Please note the single quote (\') wrapped around the passed commands.

    Examples:\n
    1. whispr run 'python main.py'\n
    2. whispr run 'bash script.sh'\n
    3. whispr run 'node server.js'\n
    4. whispr run 'semgrep ci --pro'\n
    """
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


# Secret group
@click.group()
def secret():
    """`whispr secret` group manages a secret lifecycle.

    Availble subcommands: [get, gen-random]

    Examples:\n
        # Get a secret from AWS vault\n
        1. whispr secret get --vault=aws --secret-name=my-secret --region=us-west-2 \n
        # Get a secret from Azure vault\n
        2. whispr secret get -v gcp -s my-secret -u my_vault_url\n
        # Get a secret from GCP vault\n
        3. whispr secret get -v gcp -s my-secret -p my_gcp_project_id\n
        # Generate a random string of length of 10 characters.\n
        4. whispr secret gen-random --length=10\n
        # Generate a random string of default length but exclude given characters.\n
        5. whispr secret gen-random --exclude="*;>/\'"\n
    """
    pass


# Add secret command group
cli.add_command(secret)


@click.command()
@click.option("-s", "--secret-name", nargs=1, type=click.STRING, help="Secret name to fetch from a vault")
@click.option("-v", "--vault", nargs=1, type=click.STRING, help="Vault type. Available values: aws, azure, gcp")
@click.option("-r", "--region", nargs=1, type=click.STRING, help="Region (AWS-only property)")  # AWS
@click.option("-u", "--vault-url", nargs=1, type=click.STRING, help="Vault URL (Azure-only property)")  # Azure
@click.option("-p", "--project-id", nargs=1, type=click.STRING, help="Project ID (GCP-only property)")  # GCP
def get(secret_name, vault, region, vault_url, project_id):
    """Fetches a vault secret and prints to standard output in JSON format. Output is parseable by `jq` tool. Used for quick audit of secret K:V pairs"""
    vault_secrets = get_raw_secret(
        secret_name,
        vault,
        region=region,
        vault_url=vault_url,
        project_id=project_id,
    )
    if not vault_secrets:
        return

    print(json.dumps(vault_secrets, indent=4))


@click.command()
@click.option(
    "-l",
    "--length",
    nargs=1,
    type=click.INT,
    help=f"Length of generated secret. Default is {MIN_GENERATION_LENGTH}",
)
@click.option(
    "-e",
    "--exclude",
    nargs=1,
    type=click.STRING,
    help="Characters to exclude from secret. Use Escape (\\) to escape special characters",
)
def gen_random(length, exclude):
    """Generates a crypto-secure random secret of a given length, excluding specified characters.

    Examples:\n
    # Generate a random string of length of 10 characters.\n
    1. whispr secret gen-random --length=10\n
    # Generate a random string of default length but exclude given characters.\n
    2. whispr secret gen-random --exclude="*;>/\'"\n"""

    exclude_chars = exclude
    if not exclude_chars:
        exclude_chars = ""

    if not length:
        length = MIN_GENERATION_LENGTH

    secret = generate_rand_secret(length=length, exclude_chars=exclude_chars)
    print(secret)


secret.add_command(get)
secret.add_command(gen_random)

if __name__ == "__main__":
    cli()
