import logging

import boto3
import botocore
import botocore.exceptions
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
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'ResourceNotFoundException':
                self.logger.error(f"The given secret: {secret_name} is not found on AWS. Did you set the right AWS_DEFAULT_REGION ?")
                return ""
            elif error.response['Error']['Code'] == 'UnrecognizedClientException':
                self.logger.error("Incorrect AWS credentials set for operation")
                return ""
            else:
                raise
        except Exception as e:
            self.logger.error(f"Error fetching secret: {secret_name}, Error: {e}")
            raise
