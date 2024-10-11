from dataclasses import dataclass
from ..user_token import UserToken


@dataclass
class GitHubConfig:
    token: str
    project_name: str
    project_id: str
    repo_owner: str
    repo_name: str
    field_map: dict

    def __init__(self, config_json: dict):
        """Load the configuration from a JSON file and a token from the environment"""
        name_dict = {
            'token': 'GITHUB_TOKEN',
            'token_path': 'GITHUB_TOKEN_PATH',
            'config_token': 'token',
            'config_token_path': 'token_path',
        }
        self.token = UserToken(name_dict, config_json).read()
        self.project_name = config_json.get('project')
        self.repo_owner = config_json.get('owner')
        self.repo_name = config_json.get('repo')
        self.field_map = config_json.get('fieldMap', {})
