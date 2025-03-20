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

Step 2: Initialize a whispr configuration file for AWS.

```bash
whispr init aws secrets-manager
```
or

```bash
whispr init aws parameter-store # If your secret is stored in AWS SSM parameter store
```

This creates a file called `whispr.yaml`. Update the below details.

```yaml
env_file: .env
secret_name: my-secret
vault: aws
type: secrets-manager # Another supported type is `parameter-store`
region: us-west-2 # Required for AWS
sso_profile: my_profile # Set in case if you are using a SSO profile for authentication (Enterprise developers)
```

Step 3: Define a `.env` file with secrets stored in AWS (Assuming a secret called `my-secret` with below names exist as a key value pair in AWS secrets manager)
```bash
DB_USERNAME=
DB_PASSWORD=
```

Step 4: Inject secrets into your app by running:

Let's say you want to provide vault secrets to a Node.js script named `script.js`:

```bash
whispr run 'node script.js'
```

DB_USERNAME & DB_PASSWORD are now available in script.js - `process.env`. This is very handy for development web servers.

## References:
* https://awscli.amazonaws.com/v2/documentation/api/latest/reference/sso/login.html
* https://nodejs.org/en/learn/command-line/how-to-read-environment-variables-from-nodejs
