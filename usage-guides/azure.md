## Whispr Usage Guide for Vault Type: Azure

Step 1: Authenticate to GCP using az command:

```bash
az login
```

and select the subscription where your KeyVault & secret are located. You can do that by:
```bash
az account list

az account set --subscription subscription_id
```

Step 2: Initialize a whispr configuration file for Azure.

```bash
whispr init azure
```
This creates a file called `whispr.yaml`. Update the below details.

```yaml
env_file: .env
secret_name: my-secret
vault: azure
vault_url: https://my-creds.vault.azure.net/ # Required for Azure
```

Step 3: Define a `.env` file with secrets stored in Azure (Assuming secrets with below names exist in remote secret as key value pair)
```bash
DB_USERNAME=
DB_PASSWORD=
```

Step 4: Inject secrets into your app by running:
```bash
whispr run 'node script.js'
```

DB_USERNAME & DB_PASSWORD are now available in Node.js program environment.

## References:
* https://learn.microsoft.com/en-gb/cli/azure/authenticate-azure-cli-interactively
