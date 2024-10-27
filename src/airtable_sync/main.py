import argparse
import json
import os
from .custom_logger import CustomLogger
from .github.config import GitHubConfig
from .airtable.config import AirtableConfig
from .airtable_sync import AirtableSync

logger = CustomLogger(__name__)


def parse_arguments():
    """Parse the command line arguments."""
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="A script that logs at different levels.")

    # Add mutually exclusive arguments for logging levels
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--debug', action='store_true',
                       help="Set logging level to DEBUG")
    group.add_argument('-v', '--verbose', action='store_true',
                       help="Set logging level to VERBOSE")
    group.add_argument('-i', '--info', action='store_true',
                       help="Set logging level to INFO")
    group.add_argument('-w', '--warning', action='store_true',
                       help="Set logging level to WARNING")

    # Parse the arguments
    args = parser.parse_args()

    log_level = next(
        (flag for flag in ['debug', 'verbose',
         'info', 'warning'] if getattr(args, flag)),
        'error'  # Default to ERROR
    )

    return log_level


def get_config_file_path() -> str:
    """
    Get the path to the configuration file.
    Order of lookup:
    - current working directory
    - same directory as the script
    """
    CONFIG_FILE_NAME = 'config.json'
    current_dir = os.getcwd()
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Check for the config file in the current directory first
    current_file_path = os.path.join(current_dir, CONFIG_FILE_NAME)
    if os.path.isfile(current_file_path):
        return current_file_path

    # If not found, check in the script directory
    script_file_path = os.path.join(script_dir, CONFIG_FILE_NAME)
    if os.path.isfile(script_file_path):
        return script_file_path

    raise FileNotFoundError(
        f"{CONFIG_FILE_NAME} not found in {current_dir} and {script_dir}.")


def main():
    log_level = parse_arguments()
    CustomLogger.setup_logging(log_level)

    try:
        with open(get_config_file_path()) as config_file:
            config_json = json.load(config_file)
            airtable_config = AirtableConfig(config_json.get('airtable'))
            github_config = GitHubConfig(config_json.get('github'))
    except Exception as e:
        logger.error(f"Error reading configuration file: {e}")
        return

    # Initialize the AirtableSync class and read records
    airtable_sync = AirtableSync(airtable_config, github_config)
    airtable_sync.sync()


if __name__ == "__main__":
    main()
