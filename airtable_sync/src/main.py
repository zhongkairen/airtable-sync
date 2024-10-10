import argparse
import os
from .custom_logger import CustomLogger
from .github.config import GitHubConfig
from .airtable.config import AirtableConfig
from .airtable_sync import AirtableSync


def parse_arguments():
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


def main():
    log_level = parse_arguments()
    CustomLogger.setup_logging(log_level)

    CONFIG_FILE = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'config.json')

    # Load configurations
    airtable_config = AirtableConfig(CONFIG_FILE, 'AIRTABLE_TOKEN')
    github_config = GitHubConfig(CONFIG_FILE, 'GITHUB_TOKEN')

    # Initialize the AirtableSync class and read records
    airtable_sync = AirtableSync(airtable_config, github_config)
    airtable_sync.sync()


if __name__ == "__main__":
    main()
