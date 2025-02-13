# -*- coding: utf-8 -*-

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

    SIGN = 'in'

    def to_dict(self):
        """Convert a "in" criteria to a dict"""
        return [ self.SIGN, self.fieldname, self._value ]

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
        return "(" + values + ")"

    def __str__(self):
        return f"{self.fieldname} in {self.fieldvalue}"

    def tomysql(self):
        """Convert the criteria to a SQL String compatible to MySQL Database"""
        return f"`{self.fieldname}` in {self.fieldvalue}"
