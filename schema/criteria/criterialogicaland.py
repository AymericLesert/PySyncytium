"""
This module handles a criteria linking criterias within boolean operator 'And'.
"""

from .criterialogical import DSCriteriaLogical

class DSCriteriaLogicalAnd(DSCriteriaLogical):
    """
    This class handles a criteria linking criterias within boolean operator 'And'.
    """

    SIGN = 'and'

    def to_dict(self):
        """Convert a "and" criteria to a dict"""
        return [ self.SIGN, [ criteria.to_dict() for criteria in self._criterias ] ]

    def __str__(self):
        first = True
        values = ""
        for criteria in self._criterias:
            if not first:
                values += " And "
            first = False
            values += "(" + str(criteria) + ")"
        return values
