"""
This module handles a criteria linking criterias within boolean operator.
"""

from .criteria import DSCriteria

class DSCriteriaLogical(DSCriteria):
    """
    This class handles a criteria linking criterias within boolean operator.
    """

    def __init__(self, *criterias):
        self._criterias = criterias
