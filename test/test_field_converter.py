import unittest
from datetime import datetime
from src.airtable_sync.airtable.field_converter import FieldConverter


class TestFieldConverter(unittest.TestCase):

    def test_parse_int(self):
        self.assertEqual(FieldConverter.parse(123), 123)

    def test_parse_float(self):
        self.assertEqual(FieldConverter.parse(123.45), 123.45)

    def test_parse_iso_date(self):
        self.assertEqual(FieldConverter.parse(
            "2023-10-01"), datetime(2023, 10, 1))

    def test_parse_non_iso_string(self):
        self.assertEqual(FieldConverter.parse("not a date"), "not a date")

    def test_format_datetime(self):
        self.assertEqual(FieldConverter.format(
            datetime(2023, 10, 1)), "2023-10-01")

    def test_format_int(self):
        self.assertEqual(FieldConverter.format(123), 123)

    def test_format_float(self):
        self.assertEqual(FieldConverter.format(123.45), 123.45)

    def test_format_string(self):
        self.assertEqual(FieldConverter.format("test string"), "test string")


if __name__ == '__main__':
    unittest.main()
