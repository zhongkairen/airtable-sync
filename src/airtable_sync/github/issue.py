from datetime import datetime
from enum import Enum
import re
from python_graphql_client import GraphqlClient
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
        self.github_client = None
        self.fields = {}

    def load_fields(self, base_data, fields):
        fields = fields.get('fieldValues').get('nodes')
        self.url = base_data.get('url', self.url)
        self.title = base_data.get('title')
        self.body = base_data.get('body')
        self.state = base_data.get('state')
        self.closed = base_data.get('closed')
        self.assignees = [assignee.get('login')
                          for assignee in base_data.get('assignees', {}).get('nodes', [])]
        self.labels = [label.get('name')
                       for label in base_data.get('labels', {}).get('nodes', [])]
        self.handle_field_values(fields)

    def __str__(self):
        body = self.body
        if body:
            body = body.strip().splitlines()[
                0] if body.strip() else "N/A"
        else:
            body = ""

        lines = []

        for attr in self.__dict__:
            if attr in ['url', 'title', 'body', 'assignees', 'labels', 'state', 'closed']:
                val = self.__dict__[attr]
                if attr == 'assignees':
                    val = ', '.join(val)
                elif attr == 'body':
                    val = (val.strip().splitlines()[
                           0] if val and val.strip() else "N/A")[:50]

                lines.append(f"{attr}: {val}")

        lines.extend([f"{name}: {value}" for name,
                     value in self.fields.items()])

        indent = '  '
        return '\n'.join(f"{indent}{line}" for line in lines)

    @property
    def is_epic(self):
        return self.fields.get('issue_type') == 'Epic'

    def read(self, github_client: GraphqlClient = None):
        """ CRUD - Read from URL """
        if github_client.get_issue(self.issue_number):
            logger.debug(
                f"Skipping issue {self.issue_number} as it already exists")
            return

        if github_client and not self.github_client:
            self.github_client = github_client
        query = self.github_client.query

        gql_query = query.issue(issue_number=self.issue_number)
        response = self.github_client.gql_client.execute(
            query=gql_query, headers=query.headers())

        if 'errors' in response:
            logger.error(f"Errors in response: {response}")
            raise Exception(f"Error fetching items: {response['errors']}")

        item = response['data']['repository']['issue']
        fields = item.get('projectItems', {}).get('nodes')
        first_issue_fields = (fields[0] if fields else {})
        self.load_fields(item, first_issue_fields)

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
        if field_type in [FieldType.Text, FieldType.Number, FieldType.SingleSelect]:
            return value

        if field_type == FieldType.Date:
            return GitHubIssue._parse_date(value)

        # For single select field, ignore irrelevant text such as emojis for easier comparison
        # e.g. "🚀 In progress" -> "In progress"
        # Remove non-alphanum chars and leading/trailing spaces
        if isinstance(value, str):
            value = re.sub(r'[^a-zA-Z0-9 ]', '', value).strip()

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
