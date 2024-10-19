## Whispr Usage Guide for Vault Type: AWS

Step 1: Authenticate to AWS using aws CLI.

```bash
aws sso login
```
or setup temporary AWS IAM credentials in environment like:

```bash
export AWS_ACCESS_KEY_ID=<temp_id>
export AWS_SECRET_ACCESS_KEY=<temp_secret>
export AWS_DEFAULT_REGION=<region>
```

Step 2: Initialize a whispr configuration file for GCP.

```bash
whispr init aws
```

Step 3: Define a `.env` file with secrets stored in GCP
```bash
DB_USERNAME=
DB_PASSWORD=
```

Step 4: Inject secrets into your app by running:
```bash
whispr run 'node script.js'
```

DB_USERNAME & DB_PASSWORD are now available in Node.js program environment.
