"""Collections used in Whispr"""

from enum import Enum


class VaultType(Enum):
    """Container for vault types"""

    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
