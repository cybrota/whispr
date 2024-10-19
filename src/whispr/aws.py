import logging
import json

import boto3  # AWS SDK
from whispr.vault import SimpleVault

class AWSVault(SimpleVault):
    def __init__(self, logger: logging.Logger, client: boto3.client):
        """
        Initialize the AWS Vault

        :param logger: Logger instance.
        :param client: boto3 client for AWS Secrets Manager.
        """
        super().__init__(logger, client)

    def fetch_secret(self, secret_name: str) -> str:
        """
        Fetch the secret from AWS Secrets Manager.

        :param secret_name: The name of the secret.
        :return: Secret value as a Key/Value JSON string.
        """
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            self.logger.info(f"Successfully fetched secret: {secret_name}")
            return response.get("SecretString")
        except Exception as e:
            self.logger.error(f"Error fetching secret: {secret_name}, Error: {e}")
            raise
