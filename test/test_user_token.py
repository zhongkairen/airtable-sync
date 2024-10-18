import unittest
import os
from src.airtable_sync.user_token import UserToken


class TestUserToken(unittest.TestCase):

    def setUp(self):
        self.env_vars = {
            'token': 'TEST_TOKEN',
            'token_path': 'TEST_TOKEN_PATH',
            'config_token': 'CONFIG_TEST_TOKEN',
            'config_token_path': 'CONFIG_TEST_TOKEN_PATH'
        }
        self.fallback = {
            'CONFIG_TEST_TOKEN': 'fallback_token',
            'CONFIG_TEST_TOKEN_PATH': '/path/to/fallback/token'
        }

    def test_init_with_env_token(self):
        os.environ['TEST_TOKEN'] = 'env_token_value'
        user_token = UserToken(self.env_vars, self.fallback)
        self.assertEqual(user_token.token, 'env_token_value')
        self.assertIsNone(user_token.token_path)
        del os.environ['TEST_TOKEN']

    def test_init_with_env_token_path(self):
        os.environ['TEST_TOKEN_PATH'] = '/path/to/env/token'
        user_token = UserToken(self.env_vars, self.fallback)
        self.assertEqual(user_token.token_path, '/path/to/env/token')
        self.assertIsNone(user_token.token)
        del os.environ['TEST_TOKEN_PATH']

    def test_init_with_fallback_token(self):
        user_token = UserToken(self.env_vars, self.fallback)
        self.assertEqual(user_token.token, 'fallback_token')
        self.assertEqual(user_token.token_path, '/path/to/fallback/token')

    def test_init_with_fallback_token_path(self):
        fallback = {
            'CONFIG_TEST_TOKEN': None,
            'CONFIG_TEST_TOKEN_PATH': '/path/to/fallback/token'
        }
        user_token = UserToken(self.env_vars, fallback)
        self.assertEqual(user_token.token_path, '/path/to/fallback/token')
        self.assertIsNone(user_token.token)

    def test_init_raises_environment_error(self):
        env_vars = {
            'token': 'MISSING_TOKEN',
            'token_path': 'MISSING_TOKEN_PATH',
            'config_token': 'MISSING_CONFIG_TOKEN',
            'config_token_path': 'MISSING_CONFIG_TOKEN_PATH'
        }
        fallback = {
            'MISSING_CONFIG_TOKEN': None,
            'MISSING_CONFIG_TOKEN_PATH': None
        }
        with self.assertRaises(EnvironmentError):
            UserToken(env_vars, fallback)

    def test_read_from_invalid_token_path(self):
        env_vars = {
            'token_path': 'TEST_TOKEN_PATH',
        }
        os.environ['TEST_TOKEN_PATH'] = '/path/to/invalid/token'
        fallback = {}
        with self.assertRaises(FileNotFoundError):
            token = UserToken(env_vars, fallback)
            token.read()

    def test_read_from_token_path(self):
        env_vars = {
            'token_path': 'TEST_TOKEN_PATH',
        }
        script_dir = os.path.dirname(__file__)
        token_path = os.path.join(script_dir, 'pseudo_token.txt')
        os.environ['TEST_TOKEN_PATH'] = token_path
        fallback = {}
        token = UserToken(env_vars, fallback)
        token_str = token.read()
        self.assertEqual(token_str, 'pseudo_token_value')


if __name__ == '__main__':
    unittest.main()
