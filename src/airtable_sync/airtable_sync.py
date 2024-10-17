from datetime import datetime
from .github.config import GitHubConfig
from .github.client import GitHubClient
from .github.issue import GitHubIssue
from .airtable.config import AirtableConfig
from .airtable.client import AirtableClient
from .airtable.record import AirtableRecord
from .airtable.update_result import UpdateResult
from .custom_logger import CustomLogger

logger = CustomLogger(__name__)


class AirtableSync:
    """
    AirtableSync class to synchronize records between Airtable and GitHub.
    """
    _field_map = None

    def __init__(self, airtable_config: AirtableConfig, github_config: GitHubConfig):
        self.airtable_config = airtable_config
        self.airtable = AirtableClient(airtable_config)
        self.github = GitHubClient(github_config)
        if self._field_map is None:
            self._field_map = {GitHubIssue._map_field_name(
                k): v for k, v in github_config.field_map.items()}
        # Ensure only the records in the relevant repository are synced
        self.airtable.current_repo = github_config.repo_name

    def read_records(self):
        """Read all records in Airtable"""
        self.airtable.read_records()

    def read_issues(self):
        """Read all issues in GitHub"""
        self.github.fetch_project_id()
        self.github.fetch_project_items()

    @property
    def field_map(self):
        """Map the fields between GitHub and Airtable"""
        return self._field_map

    def _verify_sync_fields(self):
        """
        Verify the fields to be synced are in the Airtable table schema.
        This method checks if all the fields synced from GitHub to Airtable exist in the Airtable table schema.
        If any fields are missing, it logs an error message listing the unknown fields and the available fields
        in the Airtable table schema.
        Returns:
            bool: True if all fields are present in the Airtable table schema, False otherwise.
        """
        missing_fields = []
        for field_name in self.field_map.values():
            if not self.airtable.field_in_schema(field_name):
                missing_fields.append(field_name)

        if missing_fields:
            def stringify(x): return ", ".join(
                [f'"{item}"' for item in x]) if isinstance(x, list) else ""
            logger.error(
                f"Unknown field(s): {stringify(missing_fields)} not found in Airtable table schema: {stringify(list(self.airtable.table_fields_schema.keys()))}.")
        return len(missing_fields) == 0

    def _verify_record_field(self):
        """
        Verifies the record field against the Airtable table fields schema.
        This method checks if the mandatory record fields are included in the table schema.
        Returns:
            tuple: A tuple containing a boolean indicating if the validation was 
            successful and an error message if it was not.
        """
        valid, error = AirtableRecord.validate_schema(
            self.airtable.table_fields_schema)
        if error:
            logger.error(error)
        return valid

    def sync(self):
        """Reconcile the records in Airtable with the issues in GitHub"""
        self._prep_sync()

        update_dict_list = []

        logger.verbose(
            f"Syncing {len(self.airtable.records_in_current_repo)} record(s) from current_repo: {self.airtable.current_repo}, of total {len(self.airtable.records)} record(s).")

        for record in self.airtable.records_in_current_repo:
            issue = self._get_issue(record)
            update_dict = self._update_fields(record, issue)
            if update_dict:
                update_dict_list.append(update_dict)

        # Perform the batch update and handle the result
        update_result = self.airtable.batch_update(update_dict_list)

        # Log the final sync result
        self._log_sync_result(update_result, logger)

    def _prep_sync(self):
        # Verify the fields to be synced
        if not (self._verify_sync_fields() and self._verify_record_field()):
            raise Exception(
                "Sync aborted due to missing fields in Airtable table schema.")

        # Read the records from Airtable
        self.read_records()

        # Read the issues from GitHub
        self.read_issues()

    def _get_issue(self, record):
        """Retrieve the GitHub issue or create one from an Airtable record."""
        return self.github.fetch_issue(record.issue_number)

    def _log_sync_result(self, sync_result: UpdateResult, logger):
        """Log the final sync result based on update counts."""
        if sync_result.error:
            logger.error(sync_result.error)

        if sync_result.updates:
            logger.verbose("\n" + sync_result.updates)

        logger.info(
            f"synced {len(self.airtable.records_in_current_repo)} record(s): {sync_result}")

    def _update_fields(self, record, issue):
        """
        Update the fields in the Airtable record (target) from the GitHub issue (source).
        Args:
            record (AirtableRecord): The Airtable record to be updated.
            issue (GitHubIssue): The GitHub issue containing the source data.
        Returns:
            dict: A dictionary containing the record's ID and updated fields.
        """
        updated_fields = {
            airtable_field: value
            for github_field, airtable_field in self.field_map.items()
            if (value := issue.fields.get(github_field)) and self.airtable.field_in_schema(airtable_field)
        }

        # Set the filtered fields to the record
        return record.set_fields(updated_fields)
