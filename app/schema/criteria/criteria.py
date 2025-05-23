# -*- coding: utf-8 -*-

"""
This module handles a select criteria.
"""

import importlib

class DSCriteria:
    """
    This class handles a criteria description.
    """

    ds_criteria_logical_and = None
    ds_criteria_logical_or = None
    ds_criteria_logical_not = None

    def to_dict(self):
        """Convert a criteria to a dict"""
        return []

    def and_(self, *items):
        """Define a boolean expression within 'and'"""
        if DSCriteria.ds_criteria_logical_and is None:
            DSCriteria.ds_criteria_logical_and = importlib.import_module('..criterialogicaland', __name__).DSCriteriaLogicalAnd
        return DSCriteria.ds_criteria_logical_and(self, *items) # pylint: disable=not-callable

    def __and__(self, item):
        """Define a boolean expression overriding '&'"""
        if DSCriteria.ds_criteria_logical_and is None:
            DSCriteria.ds_criteria_logical_and = importlib.import_module('..criterialogicaland', __name__).DSCriteriaLogicalAnd
        return DSCriteria.ds_criteria_logical_and(self, item) # pylint: disable=not-callable

    def or_(self, *items):
        """Define a boolean expression within 'or'"""
        if DSCriteria.ds_criteria_logical_or is None:
            DSCriteria.ds_criteria_logical_or = importlib.import_module('..criterialogicalor', __name__).DSCriteriaLogicalOr
        return DSCriteria.ds_criteria_logical_or(self, *items) # pylint: disable=not-callable

    def __or__(self, item):
        """Define a boolean expression overriding '|'"""
        if DSCriteria.ds_criteria_logical_or is None:
            DSCriteria.ds_criteria_logical_or = importlib.import_module('..criterialogicalor', __name__).DSCriteriaLogicalOr
        return DSCriteria.ds_criteria_logical_or(self, item) # pylint: disable=not-callable

    def not_(self):
        """Define a boolean expression overriding 'not'"""
        if DSCriteria.ds_criteria_logical_not is None:
            DSCriteria.ds_criteria_logical_not = importlib.import_module('..criterialogicalnot', __name__).DSCriteriaLogicalNot
        return DSCriteria.ds_criteria_logical_not(self) # pylint: disable=not-callable

    def tomysql(self):
        """Convert the criteria to a SQL String compatible to MySQL Database"""
        return str(self)
