"""
This module handles a comparable criteria between a field and a value.
"""

from .criteriacomparable import DSCriteriaComparable

class DSCriteriaComparableIn(DSCriteriaComparable):
    """
    This class handles a criteria checking if the value is in a list of values :
      * a field from a table,
      * a list of values.
    """

    @property
    def fieldvalue(self):
        """one of the list of values to compare"""
        values = ""
        first = True
        for value in self._value:
            if not first:
                values += ", "
            else:
                first = False
            if isinstance(value, str):
                values += "'" + value + "'"
            else:
                values += str(value)
        return "[" + values + "]"

    def __str__(self):
        return f"{self.fieldname} in {self.fieldvalue}"
