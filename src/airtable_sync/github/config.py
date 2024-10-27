from ..user_token import UserToken


class GitHubConfig:
    """Class that handles the configuration for connecting to a GitHub repository."""

    """Token string"""
    token: str
    """Project name"""
    project_name: str
    """Project ID"""
    project_id: str
    """Repository owner, e.g. 'octocat' as from github.com/octocat/Hello-World"""
    repo_owner: str
    """Repository name, e.g. 'Hello-World' as from github.com/octocat/Hello-World"""
    repo_name: str
    """Mapping of Airtable field names to GitHub issue field names"""
    field_map: dict

    def __init__(self, config_json: dict):
        # Define the names of the environment variables and configuration keys for the token
        name_dict = {
            'token': 'GITHUB_TOKEN',
            'token_path': 'GITHUB_TOKEN_PATH',
            'config_token': 'token',
            'config_token_path': 'token_path',
        }
        # Load a token from environment variable or configuration, either directly or from a file.
        self.token = UserToken(name_dict, config_json).read()

        # Load other configuration values from the config.json
        self.project_name = config_json.get('project')
        self.repo_owner = config_json.get('owner')
        self.repo_name = config_json.get('repo')
        self.field_map = config_json.get('fieldMap', {})
