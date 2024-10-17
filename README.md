# Whispr (Pronounced as Whisp-R)
A multi-vault secret injection tool for safe injection of secrets into developer environment.

# Background

MITRE ATT&CK Framework Tactic 8 (Credential Access), suggests advisories can exploit plain-text secrets and sensitive information stored in files like `.env`
and bash history (with export ENV_VAR=xyz). The `whispr` tool safely fetches and injects secrets into current shell environment without storing anything locally. In this way, developers can securely manage credentials
and mitigate advisory exploitation tacticts.


# Installation

```bash
pip install whispr
```

# Usage

First you have to configure the tool in your project from a shell:

```bash
whispr init
```
This creates a `whispr.yaml` file in your project root, with contents like this:
```yaml
secret_name: <your_secret>
vault: aws
```


# TODO

* Add tests
* Support localstack
* Support Azure Key Vault
* Support HashiCorp Vault
* Support GCP Secret Manager
* Support 1Password
