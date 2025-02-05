"""
This module handles a comparable criteria between a field and a value.
"""

from .criteriacomparable import DSCriteriaComparable

class DSCriteriaComparableEqual(DSCriteriaComparable):
    """
    This class handles an equality criteria between :
      * a field from a table,
      * a value.
    """

    SIGN = '='

    def to_dict(self):
        """Convert an equality criteria to a dict"""
        return [ self.SIGN, self.fieldname, self.fieldvalue ]

    def __str__(self):
        return f"{self.fieldname} = {self.fieldvalue}"

    def tomysql(self):
        """Convert the criteria to a SQL String compatible to MySQL Database"""
        return f"`{self.fieldname}` = {self.fieldvalue}"
