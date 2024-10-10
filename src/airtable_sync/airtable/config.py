import json
from dataclasses import dataclass
from ..user_token import UserToken

@dataclass
class AirtableConfig:
    token: str
    app_id: str
    table_id: str
    view_name: str
    
    def __init__(self, config_file: str, token_name: str):
        """Load the configuration from a JSON file and a token from the environment"""
        self.token = UserToken(token_name).read()
        with open(config_file) as file:
            config_json = json.load(file)
            airtable = config_json['airtable']
            self.app_id = airtable['baseId']
            self.table_id = airtable['tableId']
            self.view_name = airtable.get('viewName', None)
