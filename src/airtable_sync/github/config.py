import json
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

    def __init__(self, config_file: str, token_name: str):
        """Load the configuration from a JSON file and a token from the environment"""
        self.token = UserToken(token_name).read()
        with open(config_file) as file:
            config_json = json.load(file)
            github = config_json['github']
            self.project_name = github['project']
            self.repo_owner = github['owner']
            self.repo_name = github['repo']
            self.field_map = github.get('fieldMap', {})
