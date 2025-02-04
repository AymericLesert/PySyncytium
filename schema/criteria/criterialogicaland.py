"""
This module handles a criteria linking criterias within boolean operator 'And'.
"""

from .criterialogical import DSCriteriaLogical

class DSCriteriaLogicalAnd(DSCriteriaLogical):
    """
    This class handles a criteria linking criterias within boolean operator 'And'.
    """

    def __str__(self):
        first = True
        values = ""
        for criteria in self._criterias:
            if not first:
                values += " And "
            first = False
            values += "(" + str(criteria) + ")"
        return values
