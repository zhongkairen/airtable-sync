import json
import unittest
from unittest.mock import MagicMock, patch
from src.airtable_sync.airtable.client import AirtableClient
from src.airtable_sync.airtable.config import AirtableConfig
import os


class TestAirtableClient(unittest.TestCase):

    def setUp(self):
        config_json = {
            "baseId": "appM1X3TYxudtmvub",
            "tableId": "tblExnqURRZEiVMkc",
            "viewName": "Engineering Projects",
            "token": "mytoken",
            "token_path": "/path/to/airtable.pat"
        }
        self.config = AirtableConfig(config_json)
        self.client = AirtableClient(self.config)
        self.client.table = MagicMock()

    def test_table_schema(self):
        """
        AirtableClient.table_schema
        """
        expected_schema = {'fields': [{'name': 'Field1', 'type': 'text'}]}
        self.client.table.schema.return_value = expected_schema
        schema = self.client.table_schema
        self.assertEqual(schema, expected_schema)
        self.client.table.schema.assert_called_once()

    def test_table_fields_schema(self):
        """
        AirtableClient.table_fields_schema
        """
        mock_field_schema = MagicMock()
        mock_field_schema.name = 'Field1'
        mock_field_schema.type = 'text'

        mock_schema = MagicMock()
        mock_schema.fields = [mock_field_schema]
        self.client.table.schema.return_value = mock_schema
        fields_schema = self.client.table_fields_schema
        self.assertEqual(fields_schema, {'Field1': 'text'})

    def test_field_in_schema(self):
        """
        AirtableClient.field_in_schema
        """
        mock_field_schema = MagicMock()
        mock_field_schema.name = 'Field1'
        mock_field_schema.type = 'text'

        mock_schema = MagicMock()
        mock_schema.fields = [mock_field_schema]

        self.client.table.schema.return_value = mock_schema
        self.assertTrue(self.client.field_in_schema('Field1'))
        self.assertFalse(self.client.field_in_schema('Field2'))

    def test_fields_in_schema_with_json(self):
        """
        AirtableClient.field_in_schema
        """
        script_dir = os.path.dirname(__file__)
        json_file = os.path.join(
            script_dir, 'github_sync_base_table_schema.json')
        with open(json_file, 'r') as f:
            schema = json.load(f)

            def dict_to_mock(d):
                if isinstance(d, dict):
                    mock_obj = MagicMock()
                    for key, value in d.items():
                        setattr(mock_obj, key, dict_to_mock(value))
                    return mock_obj
                elif isinstance(d, list):
                    return [dict_to_mock(item) for item in d]
                else:
                    return d

            schema = dict_to_mock(schema)
            self.client.table.schema.return_value = schema
            self.assertTrue(self.client.field_in_schema(
                'Engineering Start Date'))
            self.assertTrue(self.client.field_in_schema(
                'Engineering Delivery Date'))
            self.assertTrue(self.client.field_in_schema('Issue Number'))
            self.assertFalse(self.client.field_in_schema('Field2'))
            self.assertFalse(self.client.field_in_schema('Priority'))

    @patch('src.airtable_sync.airtable.client.AirtableRecord')
    def test_read_records(self, MockAirtableRecord):
        """
        AirtableClient.read_records
        """
        self.client.table.all.return_value = [{'id': 'rec1'}, {'id': 'rec2'}]
        self.client.read_records()
        self.assertEqual(len(self.client.records), 2)
        MockAirtableRecord.assert_any_call({'id': 'rec1'})
        MockAirtableRecord.assert_any_call({'id': 'rec2'})

    def test_current_repo(self):
        """
        AirtableClient.current_repo
        """
        self.client.current_repo = 'repo1'
        self.assertEqual(self.client.current_repo, 'repo1')

    def test_records_in_current_repo(self):
        """
        AirtableClient.records_in_current_repo
        """
        record1 = MagicMock(repo_name='repo1')
        record2 = MagicMock(repo_name='repo2')
        self.client._records = [record1, record2]
        self.client.current_repo = 'repo1'
        records = self.client.records_in_current_repo
        self.assertEqual(records, [record1])

    def test_get_record_by_issue_number(self):
        """
        AirtableClient.get_record_by_issue_number
        """
        record = MagicMock(issue_number=123)
        self.client._records = [record]
        self.client.current_repo = record.repo_name
        found_record = self.client.get_record_by_issue_number(123)
        self.assertEqual(found_record, record)

    def test_get_record_by_id(self):
        """
        AirtableClient.get_record_by_id
        """
        record = MagicMock(id='rec1')
        self.client._records = [record]
        self.client.current_repo = record.repo_name
        found_record = self.client.get_record_by_id('rec1')
        self.assertEqual(found_record, record)

    @patch('src.airtable_sync.airtable.client.UpdateResult')
    def test_batch_update(self, MockUpdateResult):
        """
        AirtableClient.batch_update
        """
        record = MagicMock(id='rec1', issue_number=123)
        changes = {'field1': {'old': 'old_value', 'new': 'new_value'}}
        error = None
        record.commit_changes.return_value = (changes, error)
        self.client._records = [record]
        self.client.current_repo = record.repo_name
        self.client.table.batch_update.return_value = [
            {'id': 'rec1', 'fields': {}}]
        mock_result = MockUpdateResult.return_value

        result = self.client.batch_update([{'id': 'rec1', 'fields': {}}])
        self.assertEqual(result, mock_result)
        mock_result.add_record_status.assert_called_once()


if __name__ == '__main__':
    unittest.main()
