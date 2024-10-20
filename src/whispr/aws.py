"""AWS Secrets Manager"""

import boto3
import botocore.exceptions
import structlog

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
            self.logger.info(f"Successfully fetched aws secret: {secret_name}")
            return response.get("SecretString")
        except botocore.exceptions.ClientError as error:
            if error.response["Error"]["Code"] == "ResourceNotFoundException":
                self.logger.error(
                    "The secret is not found on AWS. Did you set the right AWS_DEFAULT_REGION ?",
                    secret_name=secret_name,
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
