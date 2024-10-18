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
        self.assertEqual(self.issue.state, 'open')
        self.assertFalse(self.issue.closed)
        self.assertEqual(self.issue.assignees, ['user1', 'user2'])
        self.assertEqual(self.issue.labels, ['bug', 'enhancement'])
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
        self.issue.state = 'open'
        self.issue.closed = False
        self.issue.assignees = ['user1', 'user2']
        self.issue.labels = ['bug', 'enhancement']
        self.issue.fields['priority'] = 'High'
        actual_strs = str(self.issue).split('\n')
        indent = ' ' * 2
        expected_strs = [
            "url: https://github.com/user/repo/issues/1",
            "title: Issue title",
            "body: Issue body",
            "assignees: user1, user2",
            "labels: bug, enhancement",
            "state: open",
            "closed: False",
            "priority: High"
        ]
        # Verify all the lines are present in the actual string
        # and the order of the lines is not important
        self.assertEqual(len(actual_strs), len(expected_strs))
        for expected_str in expected_strs:
            self.assertIn(f"{indent}{expected_str}", actual_strs)

    def test_issue_number(self):
        self.assertEqual(self.issue.issue_number, 1)


if __name__ == '__main__':
    unittest.main()