from datetime import datetime
from enum import Enum
import re
from ..custom_logger import CustomLogger

logger = CustomLogger(__name__)


class FieldType(Enum):
    Text = "TEXT"
    Number = "NUMBER"
    Date = "DATE"
    SingleSelect = "SINGLE_SELECT"
    Iteration = "ITERATION"


class GitHubIssue:
    def __init__(self, url: str):
        self.url = url
        self.fields = {}

    def load_fields(self, base_data, fields):
        fields = fields.get('fieldValues').get('nodes')
        self.url = base_data.get('url', self.url)
        self.title = base_data.get('title')
        self.body = base_data.get('body')
        self.handle_field_values(fields)

    def __str__(self):
        body = self.body
        body = (body if body else "").strip()
        body = body.splitlines()[0] if body else ""
        body = body[:50] if body else ""
        lines = []

        for attr in self.__dict__:
            if attr in ['url', 'title', 'body']:
                val = self.__dict__[attr]
                if attr == 'body':
                    val = body

                lines.append(f"{attr}: {val}")

        lines.extend([f"{name}: {value}" for name,
                     value in self.fields.items()])

        indent = '  '
        return '\n'.join(f"{indent}{line}" for line in lines)

    @property
    def is_epic(self):
        # Ignore irrelevant text such as emojis for easier comparison
        # remove non-alphanum chars and leading/trailing spaces
        # e.g. "🚀 Epic" -> "Epic"
        issue_type = self.fields.get('issue_type', '')
        issue_type = re.sub(r'[^a-zA-Z0-9 ]', '', issue_type).strip()
        return self.fields.get('issue_type') == 'Epic'

    def handle_field_values(self, field_values):
        for field_value in field_values:
            field = field_value.get('field', {})
            field_name = field.get('name')
            field_type = None
            if not field_name:
                continue
            if 'text' in field_value:
                field_type = FieldType.Text
                value = field_value['text']
            elif 'duration' in field_value and 'startDate' in field_value and 'title' in field_value:
                field_type = FieldType.Iteration
                value = f"{field_value['title']}({field_value['startDate']} - {field_value['duration']})"
            elif 'number' in field_value:
                field_type = FieldType.Number
                value = float(field_value['number'])
            elif 'date' in field_value:
                field_type = FieldType.Date
                value = field_value['date']
            elif 'name' in field_value:
                field_type = FieldType.SingleSelect
                value = field_value['name']
            else:
                logger.warning(f"unknown field type: {field_value}")
                value = None

            self._add_field(field_name, value, field_type)

    @staticmethod
    def _parse_date(date_str):
        """Parses the date string and returns a datetime object."""
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            return None

    @staticmethod
    def _map_field_name(field_name):
        """Maps the field name to an attribute name."""
        return field_name.lower().replace(" ", "_").replace("-", "_")

    @staticmethod
    def _map_field_value(field_type, value):
        """Maps the field value to a standard value."""
        if field_type == FieldType.Date:
            return GitHubIssue._parse_date(value)

        return value

    def _add_field(self, field_name, value, field_type):
        """ Add field to the issue """
        name = GitHubIssue._map_field_name(field_name)
        if name in ["title", "url"]:
            self.__dict__[name] = value
            return
        value = GitHubIssue._map_field_value(field_type, value)
        self.fields[name] = value

    @property
    def issue_number(self):
        """Extracts the issue number from the URL."""
        if self.url:
            match = re.search(r'/issues/(\d+)', self.url)
            if match:
                return int(match.group(1))
