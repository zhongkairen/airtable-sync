from ..user_token import UserToken


class AirtableConfig:
    """Class that handles the configuration for connecting to an Airtable base."""

    """Token string"""
    token: str
    """Airtable base ID"""
    app_id: str
    """Airtable table ID"""
    table_id: str
    """Airtable view name"""
    view_name: str

    def __init__(self, config_json: dict):
        # Define the names of the environment variables and configuration keys for the token
        name_dict = {
            # Environment variable names for the token
            'token': 'AIRTABLE_TOKEN',
            # Environment variable names for the token file path
            'token_path': 'AIRTABLE_TOKEN_PATH',

            # Key name in the config.json for the token
            'config_token': 'token',
            # Key name in the config.json for the token file path
            'config_token_path': 'token_path',
        }
        # Load a token from environment variable or configuration, either directly or from a file.
        self.token = UserToken(name_dict, config_json).read()

        # Load other configuration values from the config.json
        self.app_id = config_json.get('baseId')
        self.table_id = config_json.get('tableId')
        self.view_name = config_json.get('viewName')
