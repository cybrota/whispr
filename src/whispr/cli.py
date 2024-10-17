import click
import yaml
import os
import boto3

from dotenv import load_dotenv, set_key

CONFIG_FILE = 'whispr.yaml'
ENV_FILE = '.env'

@click.group()
def cli():
    pass

@click.command()
def init():
    """Creates an empty configuration YAML file."""
    config = {
        'vault': 'aws',  # Options: aws, vault, 1password
        'secret_name': '<your_secret_name>',
        # Add more configuration fields as needed for other secret managers.
    }

    if os.path.exists(CONFIG_FILE):
        click.echo(f"{CONFIG_FILE} already exists.")
    else:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as file:
            yaml.dump(config, file)
        click.echo(f"{CONFIG_FILE} has been created.")

@click.command()
def set():
    """Fetches secrets and injects them into the environment."""
    if not os.path.exists(CONFIG_FILE):
        click.echo("Configuration file not found. Run 'whispr init' first.")
        return

    # Load the configuration
    with open(CONFIG_FILE, 'r') as file:
        config = yaml.safe_load(file)

    vault = config['vault']
    secret_name = config['secret_name']

    # Fetch secret based on the vault type
    secret_value = None
    if vault == 'aws':
        secret_value = fetch_aws_secret(secret_name)
    elif vault == 'vault':
        secret_value = fetch_vault_secret(secret_name)
    elif vault == '1password':
        secret_value = fetch_1password_secret(secret_name)
    else:
        click.echo(f"Unsupported vault type: {vault}")
        return

    if secret_value:
        # Inject secret into environment or .env file
        load_dotenv(dotenv_path=ENV_FILE)
        for key, value in secret_value.items():
            set_key(ENV_FILE, key, value)
            os.environ[key] = value

        click.echo("Secrets have been injected into the environment. :)")

def fetch_aws_secret(secret_name):
    """Fetch secret from AWS Secrets Manager."""
    client = boto3.client('secretsmanager', region_name='your-region')
    try:
        response = client.get_secret_value(SecretId=secret_name)
        return response['SecretString']  # Assuming secret is in JSON format
    except Exception as e:
        click.echo(f"Error fetching secret from AWS: {e}")
        return None

def fetch_vault_secret(secret_name):
    """Fetch secret from Hashicorp Vault."""
    # Implement logic for Vault
    return None

def fetch_1password_secret(secret_name):
    """Fetch secret from 1Password."""
    # Implement logic for 1Password
    return None

cli.add_command(init)
cli.add_command(set)

if __name__ == "__main__":
    cli()
