# persistence.py

import json
import logging
import os
from typing import Any, Dict
from os.path import dirname

from whispr.server.config import CACHE_FILE
from whispr.server.encryption.encryptor import encrypt, decrypt
from whispr.server.utils.file import (
    read_file,
    write_file_atomic,
    ensure_directory_exists,
)

logger = logging.getLogger(__name__)


def save_cache(cache_data: Dict[str, Dict[str, Any]], encryption_key: str) -> None:
    """
    Serialize the entire cache dictionary, encrypt it, and write it to the designated file.

    :param cache_data: The in-memory cache (dictionary of namespaces and their key-value pairs).
    :param encryption_key: The key (derived from the JWT) to be used for encryption.
    """
    # Serialize the cache to a JSON string.
    serialized_data = json.dumps(cache_data)
    logger.debug("Cache serialized successfully.")

    # Encrypt the serialized data.
    key_bytes = encryption_key.encode("utf-8")
    encrypted_data = encrypt(serialized_data, key_bytes)
    logger.debug("Cache encrypted successfully.")

    write_file_atomic(CACHE_FILE, encrypted_data)
    logger.info("Cache successfully saved to disk at %s.", CACHE_FILE)


def load_cache(encryption_key: str) -> Dict[str, Dict[str, Any]]:
    """
    Read the encrypted cache file, decrypt it using the provided encryption key,
    deserialize it, and return the resulting cache dictionary.

    :param encryption_key: The key to be used for decryption.

    Returns:
        A cache object
    """
    # Ensure that the directory containing CACHE_FILE exists.
    ensure_directory_exists(dirname(CACHE_FILE))

    try:
        # Read the encrypted cache data.
        encrypted_data = read_file(CACHE_FILE)
        logger.debug("Encrypted cache data read from disk.")

        # Decrypt the data using the provided key.
        key_bytes = encryption_key.encode("utf-8")
        decrypted_data = decrypt(encrypted_data, key_bytes)
        logger.debug("Cache decrypted successfully.")

        # Deserialize the JSON string back to a dictionary.
        cache = json.loads(decrypted_data)
        logger.info("Cache successfully loaded from disk.")
        return cache

    except Exception as e:
        logger.error("Error loading cache: %s", e)
        return {}


def delete_cache_file() -> None:
    """
    Remove the cache file from disk.
    """
    try:
        if os.path.exists(CACHE_FILE):
            os.remove(CACHE_FILE)
            logger.info("Cache file at %s deleted successfully.", CACHE_FILE)
        else:
            logger.debug(
                "Cache file at %s does not exist; nothing to delete.", CACHE_FILE
            )
    except Exception as e:
        logger.error("Error deleting cache file: %s", e)
