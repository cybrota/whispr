# Whispr

![Logo](./logo.png)

Whispr (Pronounced as Whisp-r) is a CLI tool to safely inject secrets from your favorite secret vault (Ex: AWS Secrets Manager, Azure Key Vault etc.) into your project's shell environment. This is very useful for enabling secure local software development.
Whispr takes keys (with empty values) specified in `.env` file and fetches respective secrets from project's vault, and sets them as environment variables.

Key Features of Whispr:

* **Safe Secret Injection**: Fetch and inject secrets from your desired vault using HTTPS, SSL encryption, strict CERT validation.
* **Just In Time (JIT) Privilege**: Set environment variables for developers only when they're needed.
* **Secure Development**: Eliminate plain-text secret storage and ensure a secure development process.
* **Customizable Configurations**: Configure project-level settings to manage multiple secrets for multiple projects.
* **No Custom Scripts Required**: Whispr eliminates the need for custom scripts to manage secrets, making it easy to get started.
* **Easy Installation**: Simply install and enjoy the benefits of using Whispr.

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
secret_name: <your_secret>
vault: aws
env_file: .env
```

## Setting Up Your Secrets

**Step 2: Create or Configure a Secret File**

Create a `*.env` file (or use the `env_file` key in your `whispr.yaml` file) with empty values for your secret keys. For example:

```bash
POSTGRES_USERNAME=
POSTGRES_PASSWORD=
```

**Authenticating to Your Vault**

*   Authenticate to AWS via `aws sso login`.
*   Alternatively, set temporary AWS credentials using a config file or environment variables.

## Activating Whispr

Run the command: `whispr set` to inject your secrets into the current shell environment. Your application is now ready to launch!

# TODO

* Add tests
* Support localstack
* Support Azure Key Vault
* Support HashiCorp Vault
* Support GCP Secret Manager
* Support 1Password
