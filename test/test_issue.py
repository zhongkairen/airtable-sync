import unittest
from src.airtable_sync.github.issue import FieldType, GitHubIssue
from datetime import datetime


class TestFieldType(unittest.TestCase):
    def test_field_type_enum(self):
        self.assertEqual(FieldType.Text.value, "TEXT")
        self.assertEqual(FieldType.Number.value, "NUMBER")
        self.assertEqual(FieldType.Date.value, "DATE")
        self.assertEqual(FieldType.SingleSelect.value, "SINGLE_SELECT")
        self.assertEqual(FieldType.Iteration.value, "ITERATION")


class TestGitHubIssue(unittest.TestCase):
    def setUp(self):
        self.issue = GitHubIssue(url="https://github.com/user/repo/issues/1")

    def test_initialization(self):
        self.assertEqual(
            self.issue.url, "https://github.com/user/repo/issues/1")
        self.assertEqual(self.issue.fields, {})

    def test_load_fields(self):
        base_data = {
            'url': 'https://github.com/user/repo/issues/2',
            'title': 'Issue title',
            'body': 'Issue body',
            'state': 'open',
            'closed': False,
            'assignees': {'nodes': [{'login': 'user1'}, {'login': 'user2'}]},
            'labels': {'nodes': [{'name': 'bug'}, {'name': 'enhancement'}]}
        }
        fields = {
            'fieldValues': {
                'nodes': [
                    {'field': {'name': 'Priority'}, 'text': 'High'},
                    {'field': {'name': 'Estimate'}, 'number': 5},
                    {'field': {'name': 'Due Date'}, 'date': '2023-10-01'}
                ]
            }
        }
        self.issue.load_fields(base_data, fields)
        self.assertEqual(
            self.issue.url, 'https://github.com/user/repo/issues/2')
        self.assertEqual(self.issue.title, 'Issue title')
        self.assertEqual(self.issue.body, 'Issue body')
        self.assertEqual(self.issue.fields['priority'], 'High')
        self.assertEqual(self.issue.fields['estimate'], 5)
        self.assertEqual(self.issue.fields['due_date'], datetime.strptime(
            '2023-10-01', '%Y-%m-%d'))

    def test_is_epic(self):
        self.issue.fields['issue_type'] = 'Epic'
        self.assertTrue(self.issue.is_epic)

    def test_str(self):
        self.issue.title = 'Issue title'
        self.issue.body = 'Issue body'
        self.issue.fields['priority'] = 'High'
        actual_strs = str(self.issue).split('\n')
        indent = ' ' * 2
        expected_strs = [
            "url: https://github.com/user/repo/issues/1",
            "title: Issue title",
            "body: Issue body",
            "priority: High"
        ]
        # Verify all the lines are present in the actual string
        # and the order of the lines is not important
        self.assertEqual(len(actual_strs), len(expected_strs))
        for expected_str in expected_strs:
            self.assertIn(f"{indent}{expected_str}", actual_strs)

    def test_issue_number(self):
        self.assertEqual(self.issue.issue_number, 1)
        issue = GitHubIssue(url="https://github.com/user/repo/issue/1")
        self.assertEqual(issue.issue_number, None)
        issue = GitHubIssue(url=None)
        self.assertEqual(issue.issue_number, None)

    def test_parse_date(self):
        self.assertEqual(self.issue._parse_date('2023-10-01'),
                         datetime(2023, 10, 1))

        self.assertIsNone(self.issue._parse_date('2023-10.01'))

    def test_map_field_value(self):
        self.assertEqual(self.issue._map_field_value(
            FieldType.Text, 'value'), 'value')
        self.assertEqual(self.issue._map_field_value(
            FieldType.Number, 5), 5)
        self.assertEqual(self.issue._map_field_value(
            FieldType.Date, '2023-10-01'), datetime(2023, 10, 1))
        self.assertEqual(self.issue._map_field_value(
            FieldType.SingleSelect, 'value'), 'value')
        self.assertEqual(self.issue._map_field_value(
            FieldType.Iteration, 'value'), 'value')

    def test_handle_field_values(self):
        field_values = [
            {'field': {'name': 'Priority'}, 'text': 'High'},
            {'field': {'name': 'Estimate'}, 'number': 5},
            {'field': {'name': 'Due Date'}, 'date': '2023-10-01'},
            {'field': {'name': 'Issue type'}, 'name': 'Epic'},
            {'field': {'name': 'Stroll'}, 'title': 'w32',
                'startDate': '2023-10-01', 'duration': '2 weeks'},
            {'field': {'name': 'Unknown'}, 'temp': 1},
            {'field': {'alias': 'Tower'}, 'text': 'High'},
        ]
        self.issue._handle_field_values(field_values)
        self.assertEqual(self.issue.fields['priority'], 'High')
        self.assertEqual(self.issue.fields['estimate'], 5)
        self.assertEqual(self.issue.fields['due_date'], datetime.strptime(
            '2023-10-01', '%Y-%m-%d'))
        self.assertEqual(self.issue.fields['issue_type'], 'Epic')
        self.assertEqual(
            self.issue.fields['stroll'], 'w32(2023-10-01 - 2 weeks)')
        self.assertIsNone(self.issue.fields['unknown'])
        self.assertIsNone(self.issue.fields.get('tower'))

    def test_add_field(self):
        self.issue._add_field('Priority', 'High', FieldType.Text)
        self.assertEqual(self.issue.fields['priority'], 'High')

        self.issue._add_field('Estimate', 5, FieldType.Number)
        self.assertEqual(self.issue.fields['estimate'], 5)

        self.issue._add_field('Due Date', '2023-10-01', FieldType.Date)
        self.assertEqual(self.issue.fields['due_date'], datetime.strptime(
            '2023-10-01', '%Y-%m-%d'))

        self.issue._add_field('Issue type', 'Epic', FieldType.SingleSelect)
        self.assertEqual(self.issue.fields['issue_type'], 'Epic')

        self.issue._add_field('title', 'value', FieldType.Text)
        self.assertEqual(self.issue.title, 'value')

        self.issue._add_field('url', 'http://', FieldType.Text)
        self.assertEqual(self.issue.url, 'http://')


if __name__ == '__main__':
    unittest.main()
