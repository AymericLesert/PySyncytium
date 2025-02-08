# -*- coding: utf-8 -*-

"""
This module handles a criteria linking criterias within boolean operator 'Or'.
"""

from .criterialogical import DSCriteriaLogical

class DSCriteriaLogicalOr(DSCriteriaLogical):
    """
    This class handles a criteria linking criterias within boolean operator 'Or'.
    """

    SIGN = 'or'

    def to_dict(self):
        """Convert a "or" criteria to a dict"""
        return [ self.SIGN, [ criteria.to_dict() for criteria in self._criterias ] ]

    def __str__(self):
        first = True
        values = ""
        for criteria in self._criterias:
            if not first:
                values += " Or "
            first = False
            values += "(" + str(criteria) + ")"
        return values
