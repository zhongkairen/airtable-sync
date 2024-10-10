import os
from dotenv import load_dotenv


class UserToken:
    """Token class to read a token from the environment or a file
        If the token name ends with _PATH, the token is read from a file the path points to
        Otherwise, the token is read directly from the environment variable
    """

    load_status = load_dotenv()

    def __init__(self, name: str):
        """
        Initialize the UserToken object.
        Args:
            name (str): The name of the environment variable to retrieve. If the name ends with "_PATH",
                        it is assumed to be a path to a token file; otherwise, it is assumed to be the token itself.
        Raises:
            EnvironmentError: If neither the token path nor the token is set in the environment.
        """
        
        self.token_path = os.environ.get(name + "_PATH")
        self.token = os.environ.get(name)

        # Ensure token path set properly in the environment
        if not self.token_path and not self.token:
            raise EnvironmentError(
                f"{name} or {name}_PATH must be set in the environment")

    def read(self):
        if self.token:
            return self.token
        try:
            with open(os.path.expanduser(self.token_path), 'r') as file:
                return file.read().strip()  # Strip to remove any leading/trailing whitespace
        except Exception as e:
            raise Exception(f"Error reading token from {self.token_path}: {e}")
