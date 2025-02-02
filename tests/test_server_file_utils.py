import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from whispr.server.utils.file import (
    ensure_directory_exists,
    write_file_atomic,
    read_file,
)


class FileUtilsTestCase(unittest.TestCase):
    def setUp(self):
        # Setup test directory and file paths.
        self.test_dir = "~/test_dir"
        # We use a non-expanded path here because ensure_directory_exists calls os.path.expanduser.
        self.expanded_test_dir = os.path.expanduser(self.test_dir)
        self.test_file = os.path.join(self.expanded_test_dir, "test_file.txt")
        self.test_data = b"Sample file content."

    @patch("whispr.server.utils.file.os.path.exists")
    @patch("whispr.server.utils.file.os.makedirs")
    @patch("whispr.server.utils.file.os.chmod")
    def test_ensure_directory_exists_directory_not_exist(
        self, mock_chmod, mock_makedirs, mock_exists
    ):
        """
        Test that ensure_directory_exists creates the directory when it does not exist,
        and then sets its permissions to 0o700.
        """
        # Simulate that the directory does not exist.
        mock_exists.return_value = False

        ensure_directory_exists(self.test_dir)

        # Check that os.makedirs was called to create the directory.
        mock_makedirs.assert_called_once_with(
            os.path.expanduser(self.test_dir), mode=0o700, exist_ok=True
        )
        # Check that os.chmod was called to set the permissions.
        mock_chmod.assert_called_once_with(os.path.expanduser(self.test_dir), 0o700)
        mock_exists.assert_called_once_with(os.path.expanduser(self.test_dir))

    @patch("whispr.server.utils.file.os.path.exists")
    @patch("whispr.server.utils.file.os.makedirs")
    @patch("whispr.server.utils.file.os.chmod")
    def test_ensure_directory_exists_directory_exists(
        self, mock_chmod, mock_makedirs, mock_exists
    ):
        """
        Test that ensure_directory_exists does not try to create the directory if it already exists,
        but still resets its permissions.
        """
        # Simulate that the directory already exists.
        mock_exists.return_value = True

        ensure_directory_exists(self.test_dir)

        # os.makedirs should not be called if the directory exists.
        mock_makedirs.assert_not_called()
        # os.chmod should still be called to ensure permissions.
        mock_chmod.assert_called_once_with(os.path.expanduser(self.test_dir), 0o700)
        mock_exists.assert_called_once_with(os.path.expanduser(self.test_dir))

    def test_read_file_success(self):
        """
        Test that read_file returns the exact bytes written to a temporary file.
        """
        # Create a temporary file with known content.
        with tempfile.NamedTemporaryFile("wb", delete=False) as tmp_file:
            tmp_file.write(self.test_data)
            tmp_path = tmp_file.name

        try:
            result = read_file(tmp_path)
            self.assertEqual(result, self.test_data)
        finally:
            os.remove(tmp_path)

    def test_read_file_failure(self):
        """
        Test that read_file raises an exception when trying to read a non-existent file.
        """
        with self.assertRaises(Exception):
            read_file("non_existent_file_path")

    @patch("whispr.server.utils.file.ensure_directory_exists")
    @patch("whispr.server.utils.file.os.path.dirname")
    @patch("whispr.server.utils.file.tempfile.mkstemp")
    @patch("whispr.server.utils.file.os.fdopen")
    @patch("whispr.server.utils.file.os.chmod")
    @patch("whispr.server.utils.file.os.replace")
    def test_write_file_atomic_success(
        self,
        mock_replace,
        mock_chmod,
        mock_fdopen,
        mock_mkstemp,
        mock_dirname,
        mock_ensure_dir,
    ):
        """
        Test that write_file_atomic writes data to a temporary file,
        sets the proper permissions, and atomically replaces the target file.
        """
        # Fake file descriptor and temporary file path.
        fake_fd = 3
        fake_tmp_path = "fake_tmp_file"
        mock_mkstemp.return_value = (fake_fd, fake_tmp_path)
        # Simulate os.fdopen to return a context manager that provides a mock file object.
        mock_file_obj = MagicMock()
        mock_fdopen.return_value.__enter__.return_value = mock_file_obj
        # For simplicity, have os.path.dirname return the directory of the test file.
        mock_dirname.return_value = os.path.dirname(self.test_file)

        # Patch os.path.expanduser so that paths are returned unchanged.
        with patch(
            "whispr.server.utils.file.os.path.expanduser", side_effect=lambda x: x
        ):
            write_file_atomic(self.test_file, self.test_data)

        # Verify that ensure_directory_exists was called with the directory.
        mock_ensure_dir.assert_called_once_with(os.path.dirname(self.test_file))
        # Verify that mkstemp was called with the correct directory.
        mock_mkstemp.assert_called_once_with(dir=os.path.dirname(self.test_file))
        # Verify that the file's write method was called with our test data.
        mock_file_obj.write.assert_called_once_with(self.test_data)
        # Verify that chmod was called to set temporary file permissions.
        mock_chmod.assert_called_with(fake_tmp_path, 0o600)
        # Verify that the temporary file was atomically replaced.
        mock_replace.assert_called_once_with(fake_tmp_path, self.test_file)

    @patch("whispr.server.utils.file.ensure_directory_exists")
    @patch("whispr.server.utils.file.os.remove")
    @patch("whispr.server.utils.file.tempfile.mkstemp")
    @patch("whispr.server.utils.file.os.fdopen")
    def test_write_file_atomic_failure(
        self, mock_fdopen, mock_mkstemp, mock_remove, mock_ensure_dir
    ):
        """
        Test that write_file_atomic removes the temporary file if an error occurs during writing.
        """
        fake_fd = 3
        fake_tmp_path = "fake_tmp_file"
        mock_mkstemp.return_value = (fake_fd, fake_tmp_path)
        # Simulate an exception when writing data.
        mock_file_obj = MagicMock()
        mock_file_obj.write.side_effect = Exception("write error")
        mock_fdopen.return_value.__enter__.return_value = mock_file_obj

        with patch(
            "whispr.server.utils.file.os.path.expanduser", side_effect=lambda x: x
        ):
            with self.assertRaises(Exception) as context:
                write_file_atomic(self.test_file, self.test_data)

        self.assertIn("write error", str(context.exception))
        # Verify that the temporary file was removed.
        mock_remove.assert_called_once_with(fake_tmp_path)
