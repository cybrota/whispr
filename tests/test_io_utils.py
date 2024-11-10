
import os
import yaml
import unittest

from unittest.mock import MagicMock, patch, mock_open
from whispr.utils.io import write_to_yaml_file, load_config

class IOUtilsTestCase(unittest.TestCase):
    """Unit tests for the file utilities: write_to_yaml_file and load_config."""

    def setUp(self):
        """Set up mocks for logger and os.path methods."""
        self.mock_logger = MagicMock()
        self.config = {"key": "value"}
        self.file_path = "test_config.yaml"

    @patch("whispr.utils.io.logger", new_callable=lambda: MagicMock())
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists", return_value=False)
    def test_write_to_yaml_file_creates_file(self, mock_exists, mock_open_file, mock_logger):
        """Test that write_to_yaml_file creates a new file and writes config data as YAML."""
        write_to_yaml_file(self.config, self.file_path)

        mock_open_file.assert_called_once_with(self.file_path, "w", encoding="utf-8")
        mock_open_file().write.assert_called()  # Ensures that some content was written
        mock_logger.info.assert_called_once_with(f"{self.file_path} has been created.")

    @patch("whispr.utils.io.logger", new_callable=lambda: MagicMock())
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists", return_value=True)
    def test_write_to_yaml_file_does_not_overwrite_existing_file(self, mock_exists, mock_open_file, mock_logger):
        """Test that write_to_yaml_file does not overwrite an existing file."""
        write_to_yaml_file(self.config, self.file_path)

        mock_open_file.assert_not_called()
        mock_logger.info.assert_not_called()

    @patch("builtins.open", new_callable=mock_open, read_data="key: value")
    def test_load_config_success(self, mock_open_file):
        """Test that load_config loads a YAML file and returns a config dictionary."""
        result = load_config(self.file_path)

        mock_open_file.assert_called_once_with(self.file_path, "r", encoding="utf-8")
        self.assertEqual(result, {"key": "value"})

    @patch("builtins.open", new_callable=mock_open)
    def test_load_config_file_not_found(self, mock_open_file):
        """Test load_config raises an error if the file does not exist."""
        mock_open_file.side_effect = FileNotFoundError

        with self.assertRaises(FileNotFoundError):
            load_config("non_existent.yaml")

    @patch("builtins.open", new_callable=mock_open)
    def test_load_config_yaml_error(self, mock_open_file):
        """Test load_config raises an error for an invalid YAML file."""
        mock_open_file.side_effect = yaml.YAMLError

        with self.assertRaises(yaml.YAMLError):
            load_config(self.file_path)
