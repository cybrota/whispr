# FAQ

## How does Whispr authenticate with cloud vaults?
Whispr uses each cloud provider's standard SDK credential chain.

- AWS: IAM user/role credentials, environment variables, shared config, and optional `sso_profile`.
- Azure: `DefaultAzureCredential` chain.
- GCP: Application default credentials.

## Are secrets written to disk?
No. Whispr fetches secret payloads at runtime and injects values into a subprocess environment or command arguments. It does not persist fetched secret values to files.

## Does `no_env: true` use STDIN?
No. `no_env: true` appends secret pairs as command arguments in `KEY=VALUE` format.

## How is transport security handled?
Whispr relies on cloud SDK clients over TLS/HTTPS with certificate validation managed by the provider SDKs.

## What observability is available?
Whispr logs secret fetch events (without secret values) to the configured access log path.

## Is AWS region required?
Yes for AWS. Provide `region` in `whispr.yaml` or set `AWS_DEFAULT_REGION`.

## Which vault backends are supported today?
Currently: AWS Secrets Manager, AWS SSM Parameter Store, Azure Key Vault, and GCP Secret Manager.

## How should contributors validate changes?
Run these checks before creating a PR:

```bash
ruff check src tests
bandit -q -r src
pytest --cov=whispr tests
```
