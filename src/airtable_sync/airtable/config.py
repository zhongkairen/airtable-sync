from dataclasses import dataclass
from ..user_token import UserToken


@dataclass
class AirtableConfig:
    token: str
    app_id: str
    table_id: str
    view_name: str

    def __init__(self, config_json: dict):
        """Load the configuration from a JSON file and a token from the environment"""

        name_dict = {
            'token': 'AIRTABLE_TOKEN',
            'token_path': 'AIRTABLE_TOKEN_PATH',
            'config_token': 'token',
            'config_token_path': 'token_path',
        }
        self.token = UserToken(name_dict, config_json).read()
        self.app_id = config_json.get('baseId')
        self.table_id = config_json.get('tableId')
        self.view_name = config_json.get('viewName')
