from pyairtable import Api
from pyairtable.models.schema import FieldSchema, TableSchema
from .config import AirtableConfig
from .update_result import UpdateResult
from ..custom_logger import CustomLogger
from .record import AirtableRecord

logger = CustomLogger(__name__)


class AirtableClient:
    def __init__(self, config: AirtableConfig):
        self.config = config
        self.api = Api(self.config.token)
        self.table = self.api.table(self.config.app_id, self.config.table_id)
        self._records = []
        self._current_repo = None
        self._table_schema = None

    @property
    def table_schema(self) -> TableSchema:
        if not self._table_schema:
            self._table_schema = self.table.schema()
        return self._table_schema

    @property
    def table_fields_schema(self) -> dict:
        return {field_schema.name: field_schema.type for field_schema in self._schema_fields}

    @property
    def _schema_fields(self) -> list[FieldSchema]:
        return self.table_schema.fields

    def field_in_schema(self, field_name) -> bool:
        """Check if a field is in the Airtable schema"""
        return any(field_schema.name == field_name for field_schema in self._schema_fields)

    def read_records(self):
        """
        Reads all records from the Airtable table and stores them in the `records` attribute.
        This method fetches all entries from the Airtable table and creates a list of
        `AirtableRecord` objects by reading each entry. The resulting list is then
        assigned to the `records` attribute of the instance.
        Returns:
            None
        """
        logger.verbose(
            f"Reading Airtable records from base: {self.config.app_id} table: {self.config.table_id} view: '{self.config.view_name}'")
        self._records = [AirtableRecord(entry)
                         for entry in self.table.all(view=self.config.view_name)]

        records = "\n".join(
            [f'    {record.issue_number} {record.title}' for record in self.records])
        logger.debug(f"all records: \n{records}")

    @property
    def current_repo(self):
        return self._current_repo

    @current_repo.setter
    def current_repo(self, new_repo):
        self._current_repo = new_repo

    @property
    def records(self) -> list[AirtableRecord]:
        """
        Retrieve the list of all Airtable records in the table.

        Returns:
            list[AirtableRecord]: A list of AirtableRecord objects.
        """
        return self._records

    @property
    def records_in_current_repo(self) -> list[AirtableRecord]:
        """
        Retrieves a list of Airtable records that belong to the current repository.
        Returns:
            list[AirtableRecord]: A list of AirtableRecord objects that are associated with the current repository.
        """
        return [
            record for record in self.records if record.repo_name == self.current_repo]

    def get_record_by_id(self, id: str) -> AirtableRecord:
        """
        Find a record by its ID.
        Args:
            id (str): The ID of the record.
        Returns:
            AirtableRecord or None: The record with the specified issue number if found,
                          otherwise None.
        """
        return next((r for r in self.records_in_current_repo if r.id == id), None)

    def batch_update(self, update_dict_list) -> UpdateResult:
        """Process the batch updates and commit changes."""
        updated_record_list = self.table.batch_update(update_dict_list)

        sync_result = UpdateResult()

        for updated_record in updated_record_list:
            record_id = updated_record.get("id")
            record = self.get_record_by_id(record_id)
            issue_number = record.issue_number if record else None
            context = {'id': record_id, 'issue_number': issue_number}
            changes, error = None, None
            if not record:
                error = f"record {record_id} not found"
                status = UpdateResult.Status.FAILED
            else:
                changes, error = record.commit_changes(updated_record)
                status = UpdateResult.Status.UPDATED if changes else UpdateResult.Status.FAILED if error else UpdateResult.Status.UNCHANGED
            context.update({'changes': changes, 'error': error})
            sync_result.add_record_status(context, status)

        return sync_result
