from datetime import datetime
from urllib.parse import urlparse
from pyairtable.api.types import RecordDict
from ..custom_logger import CustomLogger

logger = CustomLogger(__name__)


class AirtableRecord:
    """Class to represent a record in Airtable."""

    """List of compulsory fields for the record."""
    _required_fields = ["Title", "Issue Link", "Issue Number"]

    """Record dictionary to store the record data."""
    _record_dict: RecordDict

    """Dictionary to store the updated fields."""
    _updated_fields: dict

    def __init__(self, record_dict: RecordDict):
        self._record_dict = record_dict
        self._updated_fields = {}

    @property
    def id(self) -> str:
        """ID of the record."""
        return self._record_dict.get("id")

    @property
    def title(self) -> str:
        """Title of the record."""
        return self._record_dict.get("fields", {}).get("Title")

    @property
    def issue_number(self) -> int:
        """Issue number in the record, corresponds to the GitHub issue number."""
        return int(self._record_dict.get("fields", {}).get("Issue Number"))

    @property
    def issue_link(self) -> str:
        """Link to the GitHub issue in the record."""
        return self._record_dict.get("fields", {}).get("Issue Link")

    @property
    def repo_name(self) -> str:
        """Repository name extracted from the issue link."""
        path_parts = urlparse(self.issue_link).path.split('/')
        if "issues" in path_parts:
            return path_parts[path_parts.index("issues") - 1]
        else:
            raise ValueError(
                "Invalid issue link format: {}".format(self.issue_link))

    @property
    def updated_fields(self) -> dict:
        """Dictionary containing the record's ID and updated fields.
            - "id": The ID of the record.
            - "fields": The updated fields of the record.
        """
        return {"id": self.id, "fields": self._updated_fields}

    def commit_changes(self, updated_record: dict) -> tuple:
        """
        Commit changes to the record by comparing the provided updated fields with the current fields.
        Args:
            updated_record (dict): A dictionary containing the updated fields and their values.
                       It should have the structure:
                       {
                           "id": <record_id>,
                           "fields": {
                           <field_name>: <field_value>,
                           ...
                           }
                       }
        Returns:
            tuple: A tuple containing a dict and an error message string.
               The dict contains all fields were successfully updated with old and new values.
               The error message provides details about any mismatches or issues encountered during the update process.
        """
        error = None
        changes = {}
        if self.id != updated_record.get("id"):
            error = f"Record ID mismatch: {updated_record.get('id')} != {self.id}"
        else:
            mismatch_fields = []
            new_values = updated_record.get("fields", {})
            committed_fields = []
            for field, expected_value in self._updated_fields.items():
                value = new_values.get(field)
                if expected_value == value:
                    old_value = self._record_dict.get("fields").get(field)
                    changes[field] = {"old": old_value, "new": value}
                    committed_fields.append(field)
                    self._record_dict.get("fields", {})[
                        field] = value  # update value
                else:
                    mismatch_fields.append(
                        {"field": field, "expected": expected_value, "actual": value})

            # Remove marked fields
            for field in committed_fields:
                self._updated_fields.pop(field, None)

            if len(mismatch_fields) > 0:
                mismatches = ', '.join(
                    f"{field['field']}: {field['expected']} != {field['actual']}" for field in mismatch_fields)
                error = f"Failed to update fields: {mismatches}."
            elif len(self._updated_fields.keys()) > 0:
                error = f"Failed to update fields: {', '.join(self._updated_fields.keys())}."
        return (changes, error)

    @staticmethod
    def validate_schema(schema: dict) -> tuple:
        """
        Validate that the provided schema contains all required fields.
        Args:
            schema (dict): The schema to validate.
        Returns:
            tuple: A tuple containing a boolean indicating if the schema is valid,
                   and an optional error message if the schema is invalid.
        """
        missing_fields = [
            field for field in AirtableRecord._required_fields if field not in schema]
        valid = len(missing_fields) == 0
        error = None if valid else f"Required fields {missing_fields} are not found in schema: {list(schema.keys())}"
        return valid, error

    def __str__(self):
        """
        String representation of the object.
        The string includes:
        - The issue number, right-justified to 5 characters.
        - The repository name.
        - The first 16 characters of the title.
        - A comma-separated list of key-value pairs from the fields dictionary.
          - If the key is "Body" and the value is a string, only the first 40 characters of the value are included, followed by ellipses.
        """

        fields_str = ', '.join(
            f"{key}: {value[:40]}..." if key == "Body" and isinstance(
                value, str) else f"{key}: {value}"
            for key, value in self._record_dict["fields"].items()
        )
        return f"{str(self.issue_number).rjust(5)} {self.repo_name} {self.title[:16]} | '{fields_str}'"

    def set_fields(self, fields: dict) -> dict:
        """
        Set multiple fields for the record.
        Args:
            fields (dict): A dictionary where keys are field names and values are the values to set.
        Returns:
            dict: A dictionary containing the record's ID and updated fields.
        """
        for field, value in fields.items():
            self._set_field(field, value)
        return self.updated_fields

    def _set_field(self, field: str, value):
        """
        Set the value of a specified field and marks it for update.
        Args:
            field (str): The name of the field to set.
            value: The value to set for the field.
        Returns:
            None
        Notes:
            - The method does not update the field value if it is the same as the current value.
        """
        current_value = self._record_dict.get("fields").get(field)
        value = self._format(value)

        if current_value == value:
            return

        logger.debug(
            f"Record {self.issue_number} fields '{field}': {current_value} -> {value}")

        if current_value is not None and not isinstance(current_value, type(value)):
            logger.warning(
                f"Field type mismatch: {field} - {current_value} != {type(value)}")
            return

        self._updated_fields[field] = value

    @staticmethod
    def _format(value):
        """
        Format the input value based on its type.
        Args:
            value: The input value to be formatted. It can be of type str, int, float, datetime, or any other type.
        Returns:
            The formatted value:
            - If `value` is a datetime object, it returns `value` formatted as a string in the "YYYY-MM-DD" format.
            - Otherwise, it returns the string representation of `value`.
        """
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")
        return value
