import os
import json
import logging
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt

from whispr.server.config import (
    TOKEN_EXPIRATION_SECONDS,
    TOKEN_ALGORITHM,
    TOKEN_DIR,
)
import whispr.server.utils.file as file_utils

# Setup logging
logger = logging.getLogger(__name__)

# Define file paths for token persistence and revocation list
TOKEN_STORAGE_FILE = os.path.join(TOKEN_DIR, "tokens.json")
REVOCATION_FILE = os.path.join(TOKEN_DIR, "revoked_tokens.json")

# In-memory cache for revoked token IDs (jti)
_revoked_tokens = set()


def _load_revoked_tokens():
    """Load the revoked tokens list from persistent storage."""
    global _revoked_tokens
    if os.path.exists(REVOCATION_FILE):
        try:
            data = file_utils.read_file(REVOCATION_FILE)
            # Expecting a JSON list of revoked jti strings.
            _revoked_tokens = set(json.loads(data))
            logger.info("Loaded revoked tokens from %s", REVOCATION_FILE)
        except Exception as e:
            logger.error("Failed to load revoked tokens: %s", e)
            _revoked_tokens = set()
    else:
        _revoked_tokens = set()


def _save_revoked_tokens():
    """Persist the revoked tokens list to storage."""
    try:
        # Convert the set to a list before saving.
        revoked_t_bytes = json.dumps(list(_revoked_tokens)).encode("utf-8")
        file_utils.write_file_atomic(REVOCATION_FILE, revoked_t_bytes)
        logger.info("Saved revoked tokens to %s", REVOCATION_FILE)
    except Exception as e:
        logger.error("Failed to save revoked tokens: %s", e)


# Initialize revoked tokens cache on module load.
_load_revoked_tokens()


def generate_token(payload: dict, secret: str) -> str:
    """
    Generate a new JWT token with the provided payload and secret.

    :param payload: JWT Payload
    :param secret: Secret to encode JWT
    Returns:
        The encoded JWT token as a string.
    """
    # Use a timezone-aware UTC datetime
    now = datetime.now(timezone.utc)
    expiration_time = now + timedelta(seconds=TOKEN_EXPIRATION_SECONDS)
    payload["exp"] = int(
        expiration_time.timestamp()
    )  # Ensure it's an integer timestamp

    # Optionally add a token identifier for revocation tracking if not already present.
    if "jti" not in payload:
        payload["jti"] = str(uuid4())

    try:
        token = jwt.encode(payload, secret, algorithm=TOKEN_ALGORITHM)
        logger.info("Generated token for jti: %s", payload["jti"])
        return token
    except Exception as e:
        logger.error("Error generating token: %s", e)
        raise


def renew_token(old_token: str, secret: str) -> str:
    """
    Renew an existing token if it is still valid.

    Validates the provided token and, if unexpired, creates a new token with an extended expiration.
    Raises:
        Exception: if the token is invalid or expired.
    Returns:
        A new JWT token string.
    """
    # Validate old token first. If invalid, validate_token will raise an exception.
    payload = validate_token(old_token, secret)

    # Remove the old expiration; you might also choose to update other session data if needed.
    payload.pop("exp", None)
    # Optionally, generate a new token id for the renewed token.
    payload["jti"] = str(uuid4())

    new_token = generate_token(payload, secret)
    logger.info("Renewed token; new jti: %s", payload["jti"])
    return new_token


def validate_token(token: str, secret: str) -> dict:
    """
    Validate the provided JWT token.

    Decodes the token, verifies its signature, expiration, and checks whether it has been revoked.
    Raises:
        jwt.ExpiredSignatureError: if the token has expired.
        jwt.InvalidTokenError: if token validation fails.
        Exception: if the token has been revoked.
    Returns:
        The decoded token payload as a dictionary.
    """
    try:
        # Decode and verify the token. This raises exceptions on errors.
        payload = jwt.decode(token, secret, algorithms=[TOKEN_ALGORITHM])
    except jwt.ExpiredSignatureError as e:
        logger.error("Token expired: %s", e)
        raise
    except jwt.InvalidTokenError as e:
        logger.error("Invalid token: %s", e)
        raise

    # Check if the token is revoked based on its unique identifier (jti).
    token_jti = payload.get("jti")
    if token_jti and is_token_revoked(token_jti):
        msg = "Token has been revoked"
        logger.error(msg)
        raise Exception(msg)

    logger.info("Validated token with jti: %s", token_jti)
    return payload


def revoke_token(token: str) -> None:
    """
    Revoke a token via administrative action.

    Validates the token to extract its unique identifier (jti) and adds it to the revocation list.
    Persists the updated revocation state.
    Raises:
        Exception: if token is invalid or if persistence fails.
    """
    try:
        # Decode without verifying expiration (if needed) to get the jti.
        # Here we use the secret if available, assuming the token structure contains a valid jti.
        # Alternatively, you can decode without verifying signature (jwt.decode(..., options={"verify_signature": False}))
        payload = jwt.decode(token, options={"verify_signature": False})
        token_jti = payload.get("jti")
        if not token_jti:
            raise Exception("Token does not contain a jti claim and cannot be revoked.")
    except Exception as e:
        logger.error("Failed to decode token for revocation: %s", e)
        raise

    _revoked_tokens.add(token_jti)
    _save_revoked_tokens()
    logger.info("Token revoked, jti: %s", token_jti)


def is_token_revoked(jti: str) -> bool:
    """
    Check if a token (by its unique identifier) has been revoked.

    Returns:
        True if the token has been revoked, False otherwise.
    """
    return jti in _revoked_tokens


def persist_token(token: str) -> None:
    """
    Persist token data to the token storage directory.

    Writes the token string (and optionally its expiration) to a file under TOKEN_STORAGE_FILE.
    Raises:
        Exception: if the persistence fails.
    """
    # Load existing tokens (if any)
    tokens = []
    if os.path.exists(TOKEN_STORAGE_FILE):
        try:
            data = file_utils.read_file(TOKEN_STORAGE_FILE)
            tokens = json.loads(data)
        except Exception as e:
            logger.warning("Could not load existing tokens, starting fresh: %s", e)

    tokens.append(token)
    try:
        t_bytes = json.dumps(tokens).encode("utf-8")
        file_utils.write_file_atomic(TOKEN_STORAGE_FILE, t_bytes)
        logger.info("Persisted token to %s", TOKEN_STORAGE_FILE)
    except Exception as e:
        logger.error("Failed to persist token: %s", e)
        raise


def load_persisted_tokens() -> list:
    """
    Load persisted tokens from the token storage directory.

    Returns:
        A list of token strings read from the storage file.
    """
    if os.path.exists(TOKEN_STORAGE_FILE):
        try:
            data = file_utils.read_file(TOKEN_STORAGE_FILE)
            tokens = json.loads(data)
            logger.info("Loaded %d persisted tokens", len(tokens))
            return tokens
        except Exception as e:
            logger.error("Failed to load persisted tokens: %s", e)
            return []
    return []
