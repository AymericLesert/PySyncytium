"""
This module handles a criteria linking criterias within boolean operator 'Not'.
"""

from .criterialogical import DSCriteriaLogical

class DSCriteriaLogicalNot(DSCriteriaLogical):
    """
    This class handles a criteria linking criterias within boolean operator 'Not'.
    """

    def __str__(self):
        return "Not (" + str(self._criterias[0]) + ")"
