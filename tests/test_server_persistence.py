import json
import unittest
from os.path import dirname
from unittest.mock import patch

from whispr.server.cache.persistence import save_cache, load_cache, delete_cache_file
from whispr.server.config import CACHE_FILE


class PersistenceTestCase(unittest.TestCase):
    def setUp(self):
        self.cache_data = {"namespace": {"key": "value"}}
        # Use a 32-character key so that its UTF-8 encoding is exactly 32 bytes.
        self.encryption_key = "a" * 32
        # Pre-serialize the cache data.
        self.serialized_data = json.dumps(self.cache_data)
        self.encryption_key_bytes = self.encryption_key.encode("utf-8")
        self.encrypted_data = b"encrypted_data"

    @patch("whispr.server.cache.persistence.write_file_atomic")
    @patch("whispr.server.cache.persistence.encrypt")
    def test_save_cache_success(self, mock_encrypt, mock_write_file_atomic):
        """
        Test that save_cache serializes the cache, encrypts it,
        and writes it atomically using write_file_atomic.
        """
        # Set up the encrypt function to return our dummy encrypted_data.
        mock_encrypt.return_value = self.encrypted_data

        save_cache(self.cache_data, self.encryption_key)

        # Verify that encrypt was called with the expected serialized data and byte key.
        mock_encrypt.assert_called_once_with(
            self.serialized_data, self.encryption_key_bytes
        )
        # Verify that write_file_atomic was called with CACHE_FILE and the encrypted data.
        mock_write_file_atomic.assert_called_once_with(CACHE_FILE, self.encrypted_data)

    @patch("whispr.server.cache.persistence.json.loads")
    @patch("whispr.server.cache.persistence.decrypt")
    @patch("whispr.server.cache.persistence.read_file")
    @patch("whispr.server.cache.persistence.ensure_directory_exists")
    def test_load_cache_success(
        self, mock_ensure_dir, mock_read_file, mock_decrypt, mock_json_loads
    ):
        """
        Test that load_cache reads the encrypted file, decrypts it,
        deserializes it, and returns the cache dictionary.
        """
        # Set up the mocks to simulate a successful load.
        mock_read_file.return_value = self.encrypted_data
        mock_decrypt.return_value = self.serialized_data
        mock_json_loads.return_value = self.cache_data

        result = load_cache(self.encryption_key)

        # Ensure that ensure_directory_exists was called with the directory of CACHE_FILE.
        mock_ensure_dir.assert_called_once_with(dirname(CACHE_FILE))
        # Verify that read_file, decrypt, and json.loads are called with the expected arguments.
        mock_read_file.assert_called_once_with(CACHE_FILE)
        mock_decrypt.assert_called_once_with(
            self.encrypted_data, self.encryption_key_bytes
        )
        mock_json_loads.assert_called_once_with(self.serialized_data)

        self.assertEqual(result, self.cache_data)

    @patch("whispr.server.cache.persistence.read_file")
    @patch("whispr.server.cache.persistence.ensure_directory_exists")
    def test_load_cache_exception_returns_empty(self, mock_ensure_dir, mock_read_file):
        """
        Test that load_cache returns an empty dict if an exception occurs
        (e.g., during file read or decryption).
        """
        # Simulate an exception when reading the file.
        mock_read_file.side_effect = Exception("read error")

        result = load_cache(self.encryption_key)
        self.assertEqual(result, {})

    @patch("whispr.server.cache.persistence.os.path.exists")
    @patch("whispr.server.cache.persistence.os.remove")
    def test_delete_cache_file_exists(self, mock_os_remove, mock_os_path_exists):
        """
        Test that delete_cache_file deletes the file if it exists.
        """
        mock_os_path_exists.return_value = True

        delete_cache_file()

        mock_os_path_exists.assert_called_once_with(CACHE_FILE)
        mock_os_remove.assert_called_once_with(CACHE_FILE)

    @patch("whispr.server.cache.persistence.os.path.exists")
    @patch("whispr.server.cache.persistence.os.remove")
    def test_delete_cache_file_not_exists(self, mock_os_remove, mock_os_path_exists):
        """
        Test that delete_cache_file does nothing if the file does not exist.
        """
        mock_os_path_exists.return_value = False

        delete_cache_file()

        mock_os_path_exists.assert_called_once_with(CACHE_FILE)
        mock_os_remove.assert_not_called()
