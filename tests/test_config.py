import unittest
from unittest.mock import patch, Mock

from app.config import Config


class TestConfigInit(unittest.TestCase):

    @patch.dict('os.environ', {'WATER_CRAWL_API_KEY': 'sys_key', 'DEBUG': 'False'})
    @patch('app.config.dotenv_values', return_value={'WATER_CRAWL_API_KEY': 'env_file_key', 'DEBUG': 'True'})
    def test_system_env_priority(self, mock_dotenv):
        """测试系统环境变量覆盖 .env 文件"""
        cfg = Config()

        # 验证系统变量覆盖
        self.assertEqual(cfg.WATER_CRAWL_API_KEY, 'sys_key')
        # 验证DEBUG取系统变量值（False）
        self.assertFalse(cfg.DEBUG)

    @patch.dict('os.environ', {})
    @patch('app.config.dotenv_values', return_value={'DEBUG': 'TRUE'})
    def test_debug_true_from_env_file(self, mock_dotenv):
        """测试从.env文件读取DEBUG=True"""
        cfg = Config()

        # 验证API_KEY不存在（返回None）
        self.assertIsNone(cfg.WATER_CRAWL_API_KEY)
        # 验证DEBUG=True
        self.assertTrue(cfg.DEBUG)

    @patch.dict('os.environ', {'DEBUG': 'invalid_value'})
    def test_invalid_debug_value(self):
        """测试无效DEBUG值的默认处理"""
        with patch('config.dotenv_values', return_value={}):
            cfg = Config()

            # 验证无效值默认False
            self.assertFalse(cfg.DEBUG)

    @patch.dict('os.environ', {})
    @patch('app.config.dotenv_values', return_value={})
    def test_no_env_vars(self, mock_dotenv):
        """测试无任何环境变量的情况"""
        cfg = Config()

        # 验证默认值
        self.assertIsNone(cfg.WATER_CRAWL_API_KEY)
        self.assertFalse(cfg.DEBUG)


if __name__ == "__main__":
    unittest.main()
