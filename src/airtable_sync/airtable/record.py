from datetime import datetime
from urllib.parse import urlparse
from pyairtable.api.types import RecordDict
from ..custom_logger import CustomLogger

logger = CustomLogger(__name__)


class FieldConverter:
    """utility class for parsing and formatting date fields in a specific format.
    todo - generalize type conversion based on field type in table schema
    """

    def iso_date_parser(x): return datetime.strptime(x, "%Y-%m-%d")
    def iso_date_formatter(x): return x.strftime("%Y-%m-%d")
    """Parser used with values in response are handled"""
    _field_parser = {
        "Start Date": iso_date_parser,
        "Delivery Date": iso_date_parser,
        "Engineering Start Date": iso_date_parser,
        "Engineering Delivery Date": iso_date_parser,
    }
    """Formatter used when passing values to request"""
    _field_formatter = {
        "Start Date": iso_date_formatter,
        "Delivery Date": iso_date_formatter,
        "Engineering Start Date": iso_date_formatter,
        "Engineering Delivery Date": iso_date_formatter,
    }

    def _generic_formatter(x):
        """
        Formats the input value based on its type.
        Args:
            x: The input value to be formatted. It can be of type str, int, float, datetime, or any other type.
        Returns:
            The formatted value:
            - If `x` is a str, int, or float, it returns `x` as is.
            - If `x` is a datetime object, it returns `x` formatted as a string in the "YYYY-MM-DD" format.
            - For any other type, it returns the string representation of `x`.
        """
        return x if isinstance(x, (str, int, float)) else x.strftime(
            "%Y-%m-%d") if isinstance(x, datetime) else str(x)

    @staticmethod
    def parse(field, value):
        """Parse values from response to internal representation"""
        return FieldConverter._field_parser.get(field, lambda x: x)(value)

    @staticmethod
    def format(field, value):
        """Format values from internal representation to request"""
        return FieldConverter._field_formatter.get(field, FieldConverter._generic_formatter)(value)


class AirtableRecord:
    """
    A class to represent a record in Airtable.
    """
    _required_fields = ["Title", "Issue Link", "Issue Number"]
    _record_dict: RecordDict
    _updated_fields: dict

    def __init__(self, record_dict: RecordDict):
        self._record_dict = record_dict
        self._updated_fields = {}

    @property
    def id(self):
        return self._record_dict.get("id")

    @property
    def title(self):
        return self._record_dict.get("fields", {}).get("Title")

    @property
    def issue_number(self) -> int:
        return int(self._record_dict.get("fields", {}).get("Issue Number"))

    @property
    def issue_link(self):
        return self._record_dict.get("fields", {}).get("Issue Link")

    @property
    def repo_name(self):
        path_parts = urlparse(self.issue_link).path.split('/')
        if "issues" in path_parts:
            return path_parts[path_parts.index("issues") - 1]
        else:
            raise ValueError(
                "Invalid issue link format: {}".format(self.issue_link))

    @property
    def updated_fields(self) -> dict:
        """
        Returns a dictionary containing the record's ID and updated fields.
        Returns:
            dict: A dictionary with two keys:
            - "id": The ID of the record.
            - "fields": The updated fields of the record.
        """
        return {"id": self.id, "fields": self._updated_fields}

    def commit_changes(self, updated_record: dict) -> tuple:
        """
        Commits changes to the record by comparing the provided updated fields with the current fields.
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
        Validates that the provided schema contains all required fields.
        Args:
            schema (dict): The schema to validate.
        Returns:
            tuple: A tuple containing a boolean indicating if the schema is valid,
                   and an optional error message if the schema is invalid.
        """
        valid = all(
            key in schema.keys() for key in AirtableRecord._required_fields)

        error = None if valid else f"Required fields {AirtableRecord._required_fields} are not found in schema: {schema.keys()}"
        return valid, error

    def __str__(self):
        """
        Returns a string representation of the object.
        The string includes the issue number (right-justified to 5 characters),
        issue link, the first 10 characters of the title, and a comma-separated
        list of key-value pairs from the fields dictionary.
        Returns:
            str: A formatted string representing the object.
        """
        fields_str = ', '.join(
            f"{key}: {value[:40]}..." if key == "Body" and isinstance(
                value, str) else f"{key}: {value}"
            for key, value in self._record_dict["fields"].items()
        )
        return f"{str(self.issue_number).rjust(5)} {self.repo_name} {self.title[:16]} | '{fields_str}'"

    def set_fields(self, fields: dict) -> dict:
        """
        Sets multiple fields for the record.
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
        Sets the value of a specified field and marks it for update.
        Args:
            field (str): The name of the field to set.
            value: The value to set for the field.
        Returns:
            None
        Notes:
            - The method does not update the field value if it is the same as the current value.
        """
        current_value = self._record_dict.get("fields").get(field)
        value = FieldConverter.format(field, value)

        if current_value == value:
            return

        logger.debug(
            f"Record {self.issue_number} fields '{field}': {current_value} -> {value}")

        if current_value is not None and type(current_value) != type(value):
            logger.warning(
                f"Field type mismatch: {field} - {current_value} != {type(value)}")
            return

        self._updated_fields[field] = value
