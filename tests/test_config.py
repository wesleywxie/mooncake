import unittest
from unittest.mock import patch, Mock

from app.config import Config


class TestConfigInit(unittest.TestCase):

    @patch.dict('os.environ', {'WATER_CRAWL_API_KEY': 'sys_key', 'DEBUG': 'False'})
    @patch('app.config.dotenv_values', return_value={'WATER_CRAWL_API_KEY': 'env_file_key', 'DEBUG': 'True'})
    def test_env_vars_from_system_override_dotenv(self, mock_dotenv):
        """System environment variables take precedence over .env file values."""
        # Act
        cfg = Config()

        # Assert
        self.assertEqual(cfg.WATER_CRAWL_API_KEY, 'sys_key')
        self.assertFalse(cfg.DEBUG)

    @patch.dict('os.environ', {}, clear=True)
    @patch('app.config.dotenv_values', return_value={'DEBUG': 'TRUE'})
    def test_debug_true_from_env_file(self, mock_dotenv):
        """DEBUG is true when provided as TRUE in .env file."""
        # Act
        cfg = Config()

        # Assert
        self.assertIsNone(cfg.WATER_CRAWL_API_KEY)
        self.assertTrue(cfg.DEBUG)

    @patch.dict('os.environ', {'DEBUG': 'invalid_value'})
    @patch('app.config.dotenv_values', return_value={})
    def test_invalid_debug_value_defaults_to_false(self, _):
        """Invalid DEBUG values fall back to False (non-debug)."""
        # Act
        cfg = Config()

        # Assert
        self.assertFalse(cfg.DEBUG)

    @patch.dict('os.environ', {}, clear=True)
    @patch('app.config.dotenv_values', return_value={})
    def test_no_env_vars_uses_defaults(self, mock_dotenv):
        """When no env vars provided, default values are used."""
        # Act
        cfg = Config()

        # Assert
        self.assertIsNone(cfg.WATER_CRAWL_API_KEY)
        self.assertFalse(cfg.DEBUG)


if __name__ == "__main__":
    unittest.main()
