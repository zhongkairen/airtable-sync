import unittest
from src.airtable_sync.airtable.record import AirtableRecord


class TestAirtableRecord(unittest.TestCase):

    def setUp(self):
        self.record_dict = {
            "id": "rec123",
            "fields": {
                "Title": "Test Issue",
                "Issue Link": "https://github.com/test/repo/issues/1",
                "Issue Number": 1
            }
        }
        self.record = AirtableRecord(self.record_dict)

    def test_id(self):
        self.assertEqual(self.record.id, "rec123")

    def test_title(self):
        self.assertEqual(self.record.title, "Test Issue")

    def test_issue_number(self):
        self.assertEqual(self.record.issue_number, 1)

    def test_issue_link(self):
        self.assertEqual(self.record.issue_link,
                         "https://github.com/test/repo/issues/1")

    def test_repo_name(self):
        self.assertEqual(self.record.repo_name, "repo")

    def test_updated_fields(self):
        self.assertEqual(self.record.updated_fields, {
                         "id": "rec123", "fields": {}})

    def test_commit_changes(self):
        updated_record = {
            "id": "rec123",
            "fields": {
                "Title": "Updated Issue",
                "Issue Number": 1
            }
        }
        self.record._updated_fields = {"Title": "Updated Issue"}
        changes, error = self.record.commit_changes(updated_record)
        self.assertEqual(
            changes, {"Title": {"old": "Test Issue", "new": "Updated Issue"}})
        self.assertIsNone(error)

    def test_commit_changes_mismatch(self):
        updated_record = {
            "id": "rec123",
            "fields": {
                "Title": "Mismatch Issue",
                "Issue Number": 1
            }
        }
        self.record._updated_fields = {"Title": "Updated Issue"}
        changes, error = self.record.commit_changes(updated_record)
        self.assertEqual(changes, {})
        self.assertIsNotNone(error)

    def test_validate_schema(self):
        schema = {
            "Title": "Test Issue",
            "Issue Link": "https://github.com/test/repo/issues/1",
            "Issue Number": 1
        }
        valid, error = AirtableRecord.validate_schema(schema)
        self.assertTrue(valid)
        self.assertIsNone(error)

    def test_validate_schema_invalid(self):
        # Missing Issue Number
        schema = {
            "Title": "Test Issue",
            "Issue Link": "https://github.com/test/repo/issues/1"
        }
        valid, error = self.record.validate_schema(schema)
        self.assertFalse(valid)
        self.assertIsNotNone(error)
        self.assertIn("Issue Number", error)

    def test_set_fields(self):
        fields = {
            "Title": "New Title",
            "Issue Number": 2
        }
        updated_fields = self.record.set_fields(fields)
        self.assertEqual(updated_fields["fields"]["Title"], "New Title")
        self.assertEqual(updated_fields["fields"]["Issue Number"], 2)

    def test_set_field(self):
        self.record._set_field("Title", "New Title")
        self.assertEqual(self.record._updated_fields["Title"], "New Title")

    def test_str(self):
        expected_str = "    1 repo Test Issue | 'Title: Test Issue, Issue Link: https://github.com/test/repo/issues/1, Issue Number: 1'"
        self.assertEqual(str(self.record), expected_str)


if __name__ == '__main__':
    unittest.main()
