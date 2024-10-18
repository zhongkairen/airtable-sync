from datetime import datetime
import re


class FieldConverter:
    """utility class for parsing and formatting date fields in a specific format.
    """

    @staticmethod
    def parse(value):
        """
        Parses the input value based on its type.
        Args:
            value: The input value to be parsed. It can be of type str, int, float, datetime, or any other type.
        Returns:
            The parsed value:
            - If `value` is an iso date text, it returns a datetime object.
            - Otherwise, it returns `value` as is.
        """
        if isinstance(value, (int, float)):
            return value
        if re.match(r"\d{4}-\d{2}-\d{2}", value):
            return datetime.strptime(value, "%Y-%m-%d")
        return value

    @staticmethod
    def format(value):
        """
        Formats the input value based on its type.
        Args:
            value: The input value to be formatted. It can be of type str, int, float, datetime, or any other type.
        Returns:
            The formatted value:
            - If `value` is a datetime object, it returns `value` formatted as a string in the "YYYY-MM-DD" format.
            - Otherwise, it returns the string representation of `value`.
        """
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")
        return value
