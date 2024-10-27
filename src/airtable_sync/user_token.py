import os


class UserToken:
    """Token class to read a token from the environment or a file
        If the token name ends with _PATH, the token is read from a file the path points to
        Otherwise, the token is read directly from the environment variable
    """

    def __init__(self, names: dict, fallback: dict):
        """
        Initialize the UserToken object.
        Args:
            name (str): The name of the environment variable to retrieve. If the name ends with "_PATH",
                        it is assumed to be a path to a token file; otherwise, it is assumed to be the token itself.
        Raises:
            EnvironmentError: If neither the token path nor the token is set in the environment.
        """
        token, token_path = names.get('token'), names.get('token_path')
        self.token = os.environ.get(token) if token else None
        self.token_path = os.environ.get(token_path) if token_path else None

        if not self.token_path and not self.token:
            config_token, config_token_path = names.get(
                'config_token'), names.get('config_token_path')
            self.token = fallback.get(config_token)
            self.token_path = fallback.get(config_token_path)
            if not self.token_path and not self.token:
                raise EnvironmentError(
                    f"{token} and {token_path} not set in the environment; {config_token} and {config_token_path} not set in the config.")

    def read(self) -> str:
        """Read the token from the environment or a file and return the token text."""
        if self.token:
            return self.token
        with open(os.path.expanduser(self.token_path), 'r') as file:
            return file.read().strip()  # Strip to remove any leading/trailing whitespace
