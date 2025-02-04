"""
This module handles a comparable criteria between a field and a value.
"""

from .criteria import DSCriteria

class DSCriteriaComparable(DSCriteria):
    """
    This class handles a comparable criteria between :
      * a field from a table,
      * a value or a list of values.
    """

    @property
    def fieldname(self):
        """field to compare"""
        return self._field.name

    @property
    def fieldvalue(self):
        """Value to compare"""
        if isinstance(self._value, str):
            return f"'{self._value}'"
        return self._value

    def __init__(self, field, value):
        self._field = field
        self._value = value
