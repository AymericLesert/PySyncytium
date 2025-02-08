# -*- coding: utf-8 -*-

"""
This module handles a comparable criteria between a field and a value.
"""

from .criteriacomparable import DSCriteriaComparable

class DSCriteriaComparableLike(DSCriteriaComparable):
    """
    This class handles a like criteria between :
      * a field from a table,
      * a value.
    """

    SIGN = 'like'

    def to_dict(self):
        """Convert a like criteria to a dict"""
        return [ self.SIGN, self.fieldname, self.fieldvalue ]

    def __str__(self):
        return f"{self.fieldname} like {self.fieldvalue}"

    def tomysql(self):
        """Convert the criteria to a SQL String compatible to MySQL Database"""
        return f"`{self.fieldname}` like {self.fieldvalue}"
