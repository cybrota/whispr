import pytest
from whispr.server.encryption import encryptor

# A dummy JWT token for testing key derivation.
TEST_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"


@pytest.fixture
def derived_key():
    """
    Fixture to derive a symmetric key from a test JWT.
    """
    return encryptor.derive_key_from_jwt(TEST_JWT)


def test_derive_key_from_jwt_returns_32_bytes(derived_key):
    """
    Test that derive_key_from_jwt returns a 32-byte key.
    """
    assert isinstance(derived_key, bytes)
    assert len(derived_key) == 32


def test_consistent_key_derivation():
    """
    Test that calling derive_key_from_jwt with the same JWT returns the same key.
    """
    jwt_token = TEST_JWT
    key1 = encryptor.derive_key_from_jwt(jwt_token)
    key2 = encryptor.derive_key_from_jwt(jwt_token)
    assert key1 == key2


def test_encrypt_decrypt_cycle(derived_key):
    """
    Test that encrypting plaintext and then decrypting returns the original message.
    """
    plaintext = "Secret Message"
    ciphertext = encryptor.encrypt(plaintext, derived_key)
    # Check that the returned ciphertext is a bytes object and longer than the nonce.
    assert isinstance(ciphertext, bytes)
    assert len(ciphertext) > 24  # assuming NONCE_SIZE is 24 bytes

    decrypted = encryptor.decrypt(ciphertext, derived_key)
    assert decrypted == plaintext


def test_decrypt_with_wrong_key(derived_key):
    """
    Test that decrypting with an incorrect key raises an exception.
    """
    plaintext = "Another Secret Message"
    ciphertext = encryptor.encrypt(plaintext, derived_key)
    # Derive a different key by using a different JWT.
    wrong_key = encryptor.derive_key_from_jwt("different_jwt_token")
    with pytest.raises(Exception, match="Decryption failed"):
        encryptor.decrypt(ciphertext, wrong_key)


def test_decrypt_tampered_ciphertext(derived_key):
    """
    Test that decryption of tampered ciphertext raises an exception.
    """
    plaintext = "Tamper Test"
    ciphertext = bytearray(encryptor.encrypt(plaintext, derived_key))
    # Tamper with the ciphertext by flipping a bit in the middle.
    ciphertext[len(ciphertext) // 2] ^= 1  # Flip one bit
    with pytest.raises(Exception, match="Decryption failed"):
        encryptor.decrypt(bytes(ciphertext), derived_key)


def test_encrypt_invalid_key_length():
    """
    Test that encryption with an invalid key length raises an exception.
    PyNaCl's SecretBox requires a 32-byte key.
    """
    invalid_key = b"short_key"
    plaintext = "Invalid key test"
    with pytest.raises(Exception, match="Encryption failed"):
        encryptor.encrypt(plaintext, invalid_key)
