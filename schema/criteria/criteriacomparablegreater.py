"""
This module handles a comparable criteria between a field and a value.
"""

from .criteriacomparable import DSCriteriaComparable

class DSCriteriaComparableGreater(DSCriteriaComparable):
    """
    This class handles a greater criteria between :
      * a field from a table,
      * a value.
    """

    def __str__(self):
        return f"{self.fieldname} > {self.fieldvalue}"
