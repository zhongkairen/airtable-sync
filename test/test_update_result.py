import unittest
from src.airtable_sync.airtable.update_result import UpdateResult


class TestUpdateResult(unittest.TestCase):

    def setUp(self):
        self.update_result = UpdateResult()

    def test_summary_no_updates(self):
        """
        UpdateResult.summary with no updates
        """
        self.assertEqual(self.update_result.summary, "")

    def test_summary_with_updated_records(self):
        """
        UpdateResult.summary with updated records
        """
        self.update_result.add_record_status(
            {'id': 'rec1', 'issue_number': 123, 'changes': {
                'field1': {'old': 'old_value', 'new': 'new_value'}}}, UpdateResult.Status.UPDATED)
        self.assertEqual(self.update_result.summary, "updated: 1")

    def test_summary_with_unchanged_records(self):
        """
        UpdateResult.summary with unchanged records
        """
        self.update_result.add_record_status(
            {'id': 'rec2', 'issue_number': 124}, UpdateResult.Status.UNCHANGED)
        self.assertEqual(self.update_result.summary, "unchanged: 1")

    def test_summary_with_failed_records(self):
        """
        UpdateResult.summary with failed records
        """
        self.update_result.add_record_status(
            {'id': 'rec3', 'issue_number': 122, 'error': 'Some error'}, UpdateResult.Status.FAILED)
        self.assertEqual(self.update_result.summary, "failed: 1")

        self.update_result.add_record_status(
            {'id': 'rec1', 'issue_number': 123, 'changes': {
                'field1': {'old': 'old_value', 'new': 'new_value'}}}, UpdateResult.Status.UPDATED)
        self.update_result.add_record_status(
            {'id': 'rec2', 'issue_number': 124}, UpdateResult.Status.UNCHANGED)
        self.update_result.add_record_status(
            {'id': 'rec3', 'issue_number': 125, 'error': 'Some error'}, UpdateResult.Status.FAILED)
        self.assertEqual(self.update_result.summary,
                         "updated: 1, unchanged: 1, failed: 2")

    def test_error_with_failed_records(self):
        """
        UpdateResult.error with failed records
        """
        self.update_result.add_record_status(
            {'id': 'rec3', 'issue_number': 125, 'error': 'Some error'}, UpdateResult.Status.FAILED)
        self.assertEqual(self.update_result.error,
                         "failed record(s): \n  Some error")

    def test_updates_with_updated_records(self):
        """
        UpdateResult.updates with updated records
        """
        self.update_result.add_record_status(
            {'id': 'rec1', 'issue_number': 123, 'changes': {
                'field1': {'old': 'old_value', 'new': 'new_value'}}}, UpdateResult.Status.UPDATED)
        self.assertEqual(self.update_result.updates,
                         "  Record - id:rec1 issue_number:123 \n    field1: old_value -> new_value")

    def test_no_error_with_no_failed_records(self):
        """
        UpdateResult.error with no failed records
        """
        self.assertIsNone(self.update_result.error)

    def test_no_updates_with_no_updated_records(self):
        """
        UpdateResult.updates with no updated records
        """
        self.assertEqual(self.update_result.updates, "")


if __name__ == '__main__':
    unittest.main()
