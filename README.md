# Whispr

![Logo](./logo.png)

Whispr (Pronounced as Whisp-r) is a CLI tool to safely inject secrets from your favorite secret vault (Ex: AWS Secrets Manager, Azure Key Vault etc.) into your app's environment. This is very useful for enabling secure local software development.

Whispr takes keys (with empty values) specified in `.env` file and fetches respective secrets from a vault, and sets them as environment variables before launching an application.

Key Features of Whispr:

* **Safe Secret Injection**: Fetch and inject secrets from your desired vault using HTTPS, SSL encryption, strict CERT validation.
* **Just In Time (JIT) Privilege**: Set environment variables for developers only when they're needed.
* **Secure Development**: Eliminate plain-text secret storage and ensure a secure development process.
* **Customizable Configurations**: Configure project-level settings to manage multiple secrets for multiple projects.
* **No Custom Scripts Required**: Whispr eliminates the need for custom bash scripts or cloud CLI tools to manage secrets, making it easy to get started.
* **Easy Installation**: Simply install Whispr from PyPi and start securing secrets.

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

Run `whispr init` in your terminal to create a `whispr.yaml` file in your project root. This file will store your configuration settings.

**Example whispr.yaml contents:**
```yaml
env_file: '.env'
secret_name: <your_secret>
vault: aws
```

## Setting Up Your Secrets

**Step 2: Create or Configure a Secret File**

Create a `.env` file (or use the `env_file` key in your `whispr.yaml` file) with empty values for your secret keys. For example:

```bash
POSTGRES_USERNAME=
POSTGRES_PASSWORD=
```

**Authenticating to Your Vault**

*   Authenticate to AWS via `aws sso login`.
*   Alternatively, set temporary AWS credentials using a config file or environment variables.

## Launching commands using Whispr

Now, you can run any app using: `whispr run '<your_app_command_with_args>'` (mind the single quotes around command) to inject your secrets before starting the subprocess.

Examples:
```bash
whispr run 'python main.py' # Inject secrets and run a Python program
whispr run 'node server.js --threads 4' # Inject secrets and run a Node.js express server
whispr run 'django manage.py runserver' # Inject secrets and start a Django server
whispr run '/bin/sh ./script.sh' # Inject secrets and run a custom bash script. Script should be permitted to execute
whispr run 'semgrep scan --pro' # Inject Semgrep App Token and scan current directory
```

# TODO

* Add tests
* Support HashiCorp Vault
* Support 1Password
