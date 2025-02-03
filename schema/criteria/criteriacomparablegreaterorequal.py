"""
This module handles a comparable criteria between a field and a value.
"""

from .criteriacomparable import DSCriteriaComparable

class DSCriteriaComparableGreaterOrEqual(DSCriteriaComparable):
    """
    This class handles a greater or equality criteria between :
      * a field from a table,
      * a value.
    """

    def __str__(self):
        return f"{self.fieldname} >= {self.fieldvalue}"
