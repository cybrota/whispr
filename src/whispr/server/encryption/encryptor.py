# encryptor.py

import nacl.secret
import nacl.utils
import nacl.hash
import nacl.encoding
from whispr.server.config import ENCRYPTION_NONCE_SIZE

def derive_key_from_jwt(jwt_token: str) -> bytes:
    """
    Derive a symmetric encryption key from the given JWT token.

    This function converts the JWT token into bytes and uses the SHA-256 hash function
    (via PyNaCl) to produce a 32-byte key suitable for use with PyNaCl's SecretBox.
    This approach is simple and can be updated later if a more robust key derivation method is needed.

    :param jwt_token (str): The JWT token which will be used as the basis for the encryption key.

    Returns:
        bytes: A 32-byte key derived from the JWT token.

    Raises:
        Exception: If key derivation fails.
    """
    try:
        token_bytes = jwt_token.encode('utf-8')
        # Use SHA-256 to produce a 32-byte key.
        key = nacl.hash.sha256(token_bytes, encoder=nacl.encoding.RawEncoder)
        return key
    except Exception as e:
        raise Exception(f"Key derivation failed: {e}") from e


def encrypt(plaintext: str, key: bytes) -> bytes:
    """
    Encrypt the given plaintext using the provided symmetric key.

    This function converts the plaintext to bytes (using UTF-8 encoding), generates a random nonce,
    initializes a SecretBox with the provided key, and encrypts the plaintext. The resulting output
    is a bytes object that includes the nonce prepended to the ciphertext.

    :param plaintext (str): The data to encrypt.
    :param key (bytes): The symmetric encryption key (typically derived from a JWT).

    Returns:
        bytes: The encrypted data containing the nonce and ciphertext.

    Raises:
        Exception: If encryption fails.
    """
    try:
        plaintext_bytes = plaintext.encode('utf-8')
        nonce = nacl.utils.random(ENCRYPTION_NONCE_SIZE)
        box = nacl.secret.SecretBox(key)
        # Encrypting with an explicit nonce; SecretBox.encrypt returns the nonce prepended to the ciphertext.
        encrypted = box.encrypt(plaintext_bytes, nonce)
        return encrypted
    except Exception as e:
        raise Exception(f"Encryption failed: {e}") from e


def decrypt(ciphertext: bytes, key: bytes) -> str:
    """
    Decrypt the provided ciphertext using the given symmetric key.

    This function initializes a SecretBox with the given key and decrypts the ciphertext,
    which is expected to have the nonce prepended. It then decodes the decrypted bytes
    back into a UTF-8 string.

    :param ciphertext (bytes): The data to decrypt, which includes the nonce as part of the data.
    :param key (bytes): The symmetric encryption key.

    Returns:
        str: The decrypted plaintext.

    Raises:
        nacl.exceptions.CryptoError: If decryption fails due to tampering or an incorrect key.
        Exception: For any other errors during decryption.
    """
    try:
        box = nacl.secret.SecretBox(key)
        # The decrypt method automatically extracts the nonce from the ciphertext.
        plaintext_bytes = box.decrypt(ciphertext)
        return plaintext_bytes.decode('utf-8')
    except Exception as e:
        raise Exception(f"Decryption failed: {e}") from e
