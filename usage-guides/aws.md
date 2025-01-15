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
whispr init aws
```

This creates a file called `whispr.yaml`. Update the below details.

```yaml
env_file: .env
secret_name: my-secret
vault: aws
region: us-west-2 # Required for AWS
sso_profile: my_profile # Set in case using a SSO profile for authentication
```

Step 3: Define a `.env` file with secrets stored in AWS (Assuming secrets with below names exist in remote secret as key value pair)
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
* https://awscli.amazonaws.com/v2/documentation/api/latest/reference/sso/login.html
