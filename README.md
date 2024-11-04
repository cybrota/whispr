[![Downloads](https://static.pepy.tech/badge/whispr/month)](https://pepy.tech/project/whispr)
[![Coverage Status](https://coveralls.io/repos/github/narenaryan/whispr/badge.svg)](https://coveralls.io/github/narenaryan/whispr)

# Whispr

![Logo](./logo.png)

Whispr (Pronounced as whisper) is a CLI tool to safely inject secrets from your favorite secret vault (Ex: AWS Secrets Manager, Azure Key Vault etc.) into your app's environment. This is very useful for enabling secure local software development.

Whispr uses keys (with empty values) specified in a `.env` file and fetches respective secrets from a vault, and sets them as environment variables before launching an application.

Key Features of Whispr:

* **Safe Secret Injection**: Fetch and inject secrets from your desired vault using HTTPS, SSL encryption, strict CERT validation.
* **Just In Time (JIT) Privilege**: Set environment variables for developers only when they're needed.
* **Secure Development**: Eliminate plain-text secret storage and ensure a secure development process.
* **Customizable Configurations**: Configure project-level settings to manage multiple secrets for multiple projects.
* **No Custom Scripts Required**: Whispr eliminates the need for custom bash scripts or cloud CLI tools to manage secrets, making it easy to get started.
* **Easy Installation**: Cross-platform installation with PyPi.

Supported Vault Technologies:

![Supported-vaults](./whispr-supported.png)


# Why use Whispr ?

The MITRE ATT&CK Framework Tactic 8 (Credential Access) suggests that adversaries can exploit plain-text secrets and sensitive information stored in files like `.env`. It is essential to avoid storing
sensitive information in unencrypted files. To help developers, Whispr can safely fetch and inject secrets from a vault into the current shell environment. This enables developers to securely manage
credentials and mitigate advisory exploitation tactics.


# Installation and Setup

## Installing Whispr

To get started with Whispr, simply run:

```bash
pip install whispr
```

## Configuring Your Project

**Step 1: Initialize Whispr**

Run `whispr init <vault_type>` in your terminal to create a `whispr.yaml` file in your project root. This file will store your configuration settings.

The available vault types are: `aws`, `azure`, and `gcp`.

**Example whispr.yaml contents (For: AWS):**
```yaml
env_file: '.env'
secret_name: <your_secret>
vault: aws
```
This default configuration will inject fetched secrets into `os.environ` of main process. If your app instead want to receive secrets as STDIN arguments, use `no_env: true` field.
This is a secure way than default control but app now should parse arguments itself.

```yaml
env_file: '.env'
secret_name: <your_secret>
vault: aws
no_env: true # Setting true will send KEY1=VAL1 secret pairs as command args
```

## Setting Up Your Injectable Secrets

**Step 2: Create or Configure a Secret File**

Create a new `.env` file with empty values for your secret keys. For example:

```bash
POSTGRES_USERNAME=
POSTGRES_PASSWORD=
```

**Note**: You can also control filename with `env_file` key in your `whispr.yaml`.

**Step 3: Authenticating to Your Vault (Ex:AWS)**

*   Authenticate to AWS using Short-term credentials.
*   Alternatively, set temporary AWS credentials using a config file or environment variables.

**Note**: Use respective authentication methods for other vaults.

## Launch any Application using Whispr

Now, you can run any app using: `whispr run '<your_app_command_with_args>'` (mind the single quotes around command) to inject your secrets before starting the subprocess.

Examples:
```bash
whispr run 'python main.py' # Inject secrets and run a Python program
whispr run 'node server.js --threads 4' # Inject secrets and run a Node.js express server
whispr run 'django manage.py runserver' # Inject secrets and start a Django server
whispr run '/bin/sh ./script.sh' # Inject secrets and run a custom bash script. Script should be permitted to execute
whispr run 'semgrep scan --pro' # Inject Semgrep App Token and scan current directory with Semgrep SAST tool.
```

## Whispr Architecture

![Supported-vaults](./whispr-arch.png)

# TODO

* Add unit tests
* Support HashiCorp Vault
* Support 1Password Vault
