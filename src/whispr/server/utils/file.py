# file.py

import os
import tempfile
import logging

logger = logging.getLogger(__name__)


def ensure_directory_exists(dir_path: str) -> None:
    """
    Ensure that the specified directory exists. If it does not exist, create it with
    permissions restricting access to only the current user (mode 0o700).

    :param dir_path (str): The directory path to check/create.

    Raises:
        Exception: Propagates any errors encountered during directory creation.
    """
    try:
        expanded_path = os.path.expanduser(dir_path)
        if not os.path.exists(expanded_path):
            os.makedirs(expanded_path, mode=0o700, exist_ok=True)
            logger.info("Directory created: %s", expanded_path)
        else:
            logger.debug("Directory already exists: %s", expanded_path)
        # Ensure the directory permissions are secure.
        os.chmod(expanded_path, 0o700)
    except Exception as e:
        logger.error("Error ensuring directory exists (%s): %s", dir_path, e)
        raise


def write_file_atomic(file_path: str, data: bytes) -> None:
    """
    Write data to a file while ensuring that the file permissions restrict access to the current user.
    The function writes data to a temporary file first for atomicity, sets the file permissions, and then
    renames the file to the final path.

    :param file_path (str): The path of the file to write.
    :param data (bytes): The data to write to the file.

    Raises:
        Exception: Propagates any errors encountered during file writing or renaming.
    """
    try:
        expanded_path = os.path.expanduser(file_path)
        directory = os.path.dirname(expanded_path)
        ensure_directory_exists(directory)

        # Create a temporary file in the same directory for atomic write.
        fd, tmp_path = tempfile.mkstemp(dir=directory)
        try:
            with os.fdopen(fd, "wb") as tmp_file:
                tmp_file.write(data)
            logger.debug("Data written to temporary file: %s", tmp_path)

            # Set file permissions to owner read/write only (mode 0o600).
            os.chmod(tmp_path, 0o600)
            logger.debug("Temporary file permissions set to 0o600: %s", tmp_path)

            # Atomically replace the target file with the temporary file.
            os.replace(tmp_path, expanded_path)
            logger.info("Secure file written atomically to: %s", expanded_path)
        except Exception as e:
            # Remove the temporary file if an error occurs.
            os.remove(tmp_path)
            logger.error("Error writing secure file (temporary file removed): %s", e)
            raise
    except Exception as e:
        logger.error("Error in write_secure_file for %s: %s", file_path, e)
        raise


def read_file(file_path: str) -> bytes:
    """
    Read and return the contents of the specified file as bytes.

    :param file_path (str): The path to the file to read.

    Returns:
        bytes: The contents of the file.

    Raises:
        Exception: If the file does not exist or cannot be read.
    """
    expanded_path = os.path.expanduser(file_path)
    try:
        with open(expanded_path, "rb") as f:
            data = f.read()
            logger.debug("Read %d bytes from file: %s", len(data), expanded_path)
            return data
    except Exception as e:
        logger.error("Error reading file %s: %s", file_path, e)
        raise
