"""Collections used in Whispr"""

from enum import Enum


class VaultType(Enum):
    """Container for vault types"""

    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"


class AWSVaultSubType(Enum):
    """Container for AWS vault sub-types"""

    SECRETS_MANAGER = "secrets-manager"
    PARAMETER_STORE = "parameter-store"
