import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
from src.airtable_sync.airtable_sync import AirtableSync
from src.airtable_sync.github.config import GitHubConfig
from src.airtable_sync.airtable.config import AirtableConfig
from src.airtable_sync.airtable.record import AirtableRecord
from src.airtable_sync.airtable.update_result import UpdateResult
from src.airtable_sync.github.issue import GitHubIssue


class TestAirtableSync(unittest.TestCase):
    def setUp(self):
        airtable_config_json = {
            "token": "fake_token",
            "baseId": "fake_base_id",
            "tableId": "fake_table",
            "viewName": "fake_view"
        }
        airtable_config = AirtableConfig(airtable_config_json)
        github_config_json = {
            "owner": "fake_owner",
            "repo": "fake_repo",
            "project": "fake_project",
            "token": "fake_token",
            "fieldMap": {"priority": "Priority"}
        }
        github_config = GitHubConfig(github_config_json)
        self.sync = AirtableSync(airtable_config, github_config)
        self.sync.airtable = MagicMock()
        self.sync.github = MagicMock()

    def test_read_records(self):
        self.sync.read_records()
        self.sync.airtable.read_records.assert_called_once()

    def test_read_issues(self):
        self.sync.read_issues()
        self.sync.github.fetch_project_id.assert_called_once()
        self.sync.github.fetch_project_items.assert_called_once()

    def test_field_map(self):
        expected_field_map = {"priority": "Priority"}
        self.assertEqual(self.sync.field_map, expected_field_map)

    def test_verify_sync_fields(self):
        self.sync.airtable.field_in_schema = MagicMock(return_value=True)
        self.assertTrue(self.sync._verify_sync_fields())

    @patch('src.airtable_sync.airtable_sync.AirtableRecord.validate_schema')
    def test_verify_record_field(self, mock_validate_schema):
        mock_validate_schema.return_value = (True, None)
        self.assertTrue(self.sync._verify_record_field())

    def test_sync(self):
        self.sync._prep_sync = MagicMock()
        self.sync._get_issue = MagicMock(return_value=GitHubIssue(
            url="https://github.com/user/repo/issues/1"))
        self.sync._update_fields = MagicMock(
            return_value={"id": "rec123", "fields": {"Priority": "High"}})
        self.sync.airtable.batch_update = MagicMock(
            return_value=MagicMock(updates="1 record updated", error=None))
        self.sync._log_sync_result = MagicMock()

        record_dict = {"id": "rec123", "fields": {"Issue Number": 1}}
        self.sync.airtable.records_in_current_repo = [
            AirtableRecord(record_dict)]

        self.sync.sync()

        self.sync._prep_sync.assert_called_once()
        self.sync._get_issue.assert_called_once()
        self.sync._update_fields.assert_called_once()
        self.sync.airtable.batch_update.assert_called_once()
        self.sync._log_sync_result.assert_called_once()

    def test_prep_sync(self):
        self.sync._verify_sync_fields = MagicMock(return_value=True)
        self.sync._verify_record_field = MagicMock(return_value=True)
        self.sync.read_records = MagicMock()
        self.sync.read_issues = MagicMock()

        self.sync._prep_sync()

        self.sync._verify_sync_fields.assert_called_once()
        self.sync._verify_record_field.assert_called_once()
        self.sync.read_records.assert_called_once()
        self.sync.read_issues.assert_called_once()

    def test_get_issue(self):
        record_dict = {"id": "rec123", "fields": {"Issue Number": 1}}
        record = AirtableRecord(record_dict)
        self.sync.github.fetch_issue = MagicMock(
            return_value=GitHubIssue(url="https://github.com/user/repo/issues/1"))

        issue = self.sync._get_issue(record)
        self.sync.github.fetch_issue.assert_called_once_with(1)
        self.assertIsInstance(issue, GitHubIssue)

    def test_log_sync_result(self):
        sync_result = MagicMock()
        sync_result.error = None
        sync_result.updates = None
        logger = MagicMock()
        self.sync._log_sync_result(sync_result, logger)
        logger.info.assert_called_once()
        logger.error.assert_not_called()
        logger.verbose.assert_not_called()

        logger = MagicMock()
        sync_result = MagicMock()
        sync_result.error = "Some error"
        sync_result.updates = None
        self.sync._log_sync_result(sync_result, logger)
        logger.info.assert_called_once()
        logger.error.assert_called_once()
        logger.verbose.assert_not_called()

        logger = MagicMock()
        sync_result = MagicMock()
        sync_result.error = "Some error"
        sync_result.updates = "None"
        self.sync._log_sync_result(sync_result, logger)
        logger.info.assert_called_once()
        logger.error.assert_called_once()
        logger.verbose.assert_called_once()

    def test_update_fields(self):
        record_dict = {"id": "rec123", "fields": {"Issue Number": 1}}
        record = AirtableRecord(record_dict)
        issue = GitHubIssue(url="https://github.com/user/repo/issues/1")
        issue.fields = {"priority": "High"}

        self.sync.airtable.field_in_schema = MagicMock(return_value=True)
        updated_fields = self.sync._update_fields(record, issue)

        self.assertEqual(updated_fields, {
                         "id": "rec123", "fields": {"Priority": "High"}})


if __name__ == '__main__':
    unittest.main()
