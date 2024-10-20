import unittest
from unittest.mock import patch, mock_open, MagicMock
import argparse
from src.airtable_sync.main import parse_arguments, get_config_file_path, main


class TestMain(unittest.TestCase):

    @patch('argparse.ArgumentParser.parse_args')
    def test_parse_arguments(self, mock_parse_args):
        mock_parse_args.return_value = argparse.Namespace(
            debug=True, verbose=False, info=False, warning=False)
        self.assertEqual(parse_arguments(), 'debug')

        mock_parse_args.return_value = argparse.Namespace(
            debug=False, verbose=True, info=False, warning=False)
        self.assertEqual(parse_arguments(), 'verbose')

        mock_parse_args.return_value = argparse.Namespace(
            debug=False, verbose=False, info=True, warning=False)
        self.assertEqual(parse_arguments(), 'info')

        mock_parse_args.return_value = argparse.Namespace(
            debug=False, verbose=False, info=False, warning=True)
        self.assertEqual(parse_arguments(), 'warning')

        mock_parse_args.return_value = argparse.Namespace(
            debug=False, verbose=False, info=False, warning=False)
        self.assertEqual(parse_arguments(), 'error')

    @patch('os.path.isfile')
    @patch('os.getcwd')
    @patch('os.path.dirname')
    @patch('os.path.abspath')
    def test_get_config_file_path(self, mock_abspath, mock_dirname, mock_getcwd, mock_isfile):
        mock_getcwd.return_value = '/current/dir'
        mock_abspath.return_value = '/script/dir/main.py'
        mock_dirname.return_value = '/script/dir'

        # Test when config file is in the current directory
        mock_isfile.side_effect = lambda path: path == '/current/dir/config.json'
        self.assertEqual(get_config_file_path(), '/current/dir/config.json')

        # Test when config file is in the script directory
        mock_isfile.side_effect = lambda path: path == '/script/dir/config.json'
        self.assertEqual(get_config_file_path(), '/script/dir/config.json')

        # Test when config file is not found
        mock_isfile.side_effect = lambda path: False
        with self.assertRaises(FileNotFoundError):
            get_config_file_path()

    @patch('builtins.open', new_callable=mock_open, read_data='{"airtable": {}, "github": {}}')
    @patch('json.load')
    @patch('src.airtable_sync.main.CustomLogger.setup_logging')
    @patch('src.airtable_sync.main.get_config_file_path')
    @patch('src.airtable_sync.main.AirtableConfig')
    @patch('src.airtable_sync.main.GitHubConfig')
    @patch('src.airtable_sync.main.AirtableSync')
    def test_main(self, mock_airtable_sync, mock_github_config, mock_airtable_config, mock_get_config_file_path, mock_setup_logging, mock_json_load, mock_open):
        mock_get_config_file_path.return_value = '/path/to/config.json'
        mock_json_load.return_value = {'airtable': {}, 'github': {}}

        mock_airtable_sync_instance = MagicMock()
        mock_airtable_sync.return_value = mock_airtable_sync_instance

        with patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(debug=True)):
            main()

        mock_setup_logging.assert_called_once_with('debug')
        mock_open.assert_called_once_with('/path/to/config.json')
        mock_json_load.assert_called_once()
        mock_airtable_config.assert_called_once_with({})
        mock_github_config.assert_called_once_with({})
        mock_airtable_sync.assert_called_once_with(
            mock_airtable_config(), mock_github_config())
        mock_airtable_sync_instance.sync.assert_called_once()


if __name__ == '__main__':
    unittest.main()
