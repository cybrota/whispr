"""AWS Secrets Manager"""

import boto3
import botocore.exceptions
import structlog

from whispr.logging import log_secret_fetch
from whispr.vault import SimpleVault


class AWSVault(SimpleVault):
    """A Vault that maps secrets in AWS secrets manager"""

    def __init__(self, logger: structlog.BoundLogger, client: boto3.client):
        """
        Initialize the AWS Vault

        :param logger: Logger instance.
        :param client: boto3 client for AWS Secrets Manager.
        """
        super().__init__(logger, client)

    def fetch_secrets(self, secret_name: str) -> str:
        """
        Fetch the secret from AWS Secrets Manager.

        :param secret_name: The name of the secret.
        :return: Secret value as a Key/Value JSON string.
        """
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            secret_value = response.get("SecretString") or ""
            self.logger.debug(f"Successfully fetched aws secret: {secret_name}")
            if secret_value:
                log_secret_fetch(self.logger, secret_name, "aws")
            return secret_value
        except botocore.exceptions.ClientError as error:
            if error.response["Error"]["Code"] == "ResourceNotFoundException":
                self.logger.error(
                    "The secret is not found on AWS. Did you set the right AWS_DEFAULT_REGION ?",
                    secret_name=secret_name,
                    region=self.client.meta.region_name,
                )
                return ""
            elif error.response["Error"]["Code"] == "UnrecognizedClientException":
                self.logger.error(
                    "Incorrect AWS credentials set for operation. Please verify them and retry."
                )
                return ""
            else:
                raise
        except Exception as e:
            self.logger.error("Error fetching secret", error=e)
            raise


class AWSSSMVault(SimpleVault):
    """A Vault that maps secrets in AWS SSM parameter store"""

    def __init__(self, logger: structlog.BoundLogger, client: boto3.client):
        """
        Initialize the AWS Vault

        :param logger: Logger instance.
        :param client: boto3 client for AWS Secrets Manager.
        """
        super().__init__(logger, client)

    def fetch_secrets(self, secret_name: str) -> str:
        """
        Fetch the secret from AWS Secrets Manager.

        :param secret_name: The name of the secret.
        :return: Secret value as a Key/Value JSON string.
        """
        try:
            response = self.client.get_parameter(Name=secret_name)
            param = response.get("Parameter")
            if param:
                secret_value = param.get("Value") or ""
                if secret_value:
                    log_secret_fetch(self.logger, secret_name, "aws-ssm")
                return secret_value
            return ""
        except botocore.exceptions.ClientError as error:
            if error.response["Error"]["Code"] == "ParameterNotFound":
                self.logger.error(
                    "The secret is not found on AWS Parameter store. Did you set the right AWS_DEFAULT_REGION ?",
                    secret_name=secret_name,
                    region=self.client.meta.region_name,
                )
                return ""
            elif error.response["Error"]["Code"] == "UnrecognizedClientException":
                self.logger.error(
                    "Incorrect AWS credentials set for operation. Please verify them and retry."
                )
                return ""
            else:
                raise
        except Exception as e:
            self.logger.error("Error fetching secret", error=e)
            raise
