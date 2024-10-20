import unittest
from unittest.mock import MagicMock
from src.airtable_sync.github.client import GitHubClient
from src.airtable_sync.github.config import GitHubConfig
from src.airtable_sync.github.issue import GitHubIssue


class TestGitHubClient(unittest.TestCase):

    def setUp(self):
        config_data = {
            "project_name": "Test Project",
            "project_id": "12345",
            "token": "fake_token"
        }
        self.config = GitHubConfig(config_data)
        self.client = GitHubClient(self.config)
        self.client._client = MagicMock()
        self.client._query = MagicMock()
        self.client.epic_issues = []

    def test_fetch_project_id(self):
        self.config.project_name = 'Test Project'
        response = {
            'data': {
                'repository': {
                    'projectsV2': {
                        'nodes': [
                            {'title': 'Test Project', 'id': '12345'}
                        ]
                    }
                }
            }
        }
        self.client._client.execute.return_value = response
        self.client.fetch_project_id()
        self.assertEqual(self.config.project_id, '12345')

    def test_fetch_project_id_error(self):
        response = {'errors': ['Some error']}
        self.client._client.execute.return_value = response
        with self.assertRaises(Exception):
            self.client.fetch_project_id()

    def test_fetch_project_items(self):
        self.config.project_id = '12345'
        response = {
            'data': {
                'node': {
                    'items': {
                        'nodes': [],
                        'pageInfo': {
                            'hasNextPage': False,
                            'endCursor': None
                        }
                    }
                }
            }
        }
        self.client._client.execute.return_value = response
        self.client.fetch_project_items()
        self.assertEqual(len(self.client.epic_issues), 0)

    def test_fetch_issue(self):
        issue_number = 1
        response = {
            'data': {
                'repository': {
                    'issue': {
                        'url': 'https://github.com/test/repo/issues/1',
                        'projectItems': {
                            'nodes': [
                                {
                                    'fieldValues': {
                                        'nodes': [
                                            {'field': {'name': 'Issue Type'},
                                                'text': 'Epic'}
                                        ]
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        }
        self.client._client.execute.return_value = response
        issue = self.client.fetch_issue(issue_number)
        self.assertIsInstance(issue, GitHubIssue)
        self.assertEqual(issue.url, 'https://github.com/test/repo/issues/1')

    def test_get_issue(self):
        issue_number = 1
        issue = GitHubIssue(
            url=f'https://github.com/test/repo/issues/{issue_number}')
        self.client.epic_issues.append(issue)
        found_issue = self.client.get_issue(issue_number)
        self.assertEqual(found_issue, issue)

    def test_handle_issues_data(self):
        def make_issue(issue_number, is_epic):
            return {
                'content': {
                    'url': f'https://github.com/test/repo/issues/{issue_number}',
                },
                'fieldValues': {
                    'nodes': [
                        {'field': {'name': 'Issue Type'}, 'text': (
                            'Epic' if is_epic else 'Task')}
                    ]
                }
            }

        items = [
            make_issue(1, False),
            make_issue(2, True),
            make_issue(3, False),
            make_issue(4, True),
            make_issue(5, False),
            make_issue(6, True)
        ]
        self.client._handle_issues_data(items)
        self.assertEqual(len(self.client.epic_issues), 3)
        epic_issue_numbers = [
            issue.issue_number for issue in self.client.epic_issues]
        self.assertIn(2, epic_issue_numbers)
        self.assertIn(4, epic_issue_numbers)
        self.assertIn(6, epic_issue_numbers)


if __name__ == '__main__':
    unittest.main()
