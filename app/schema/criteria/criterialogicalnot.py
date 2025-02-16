# -*- coding: utf-8 -*-

"""
This module handles a criteria linking criterias within boolean operator 'Not'.
"""

from .criterialogical import DSCriteriaLogical

class DSCriteriaLogicalNot(DSCriteriaLogical):
    """
    This class handles a criteria linking criterias within boolean operator 'Not'.
    """

    SIGN = 'not'

    def to_dict(self):
        """Convert a "not" criteria to a dict"""
        return [ self.SIGN, self._criterias[0].to_dict() ]

    def __str__(self):
        return "Not (" + str(self._criterias[0]) + ")"
