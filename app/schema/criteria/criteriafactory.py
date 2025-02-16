# -*- coding: utf-8 -*-

"""Create a criteria from a dictionary"""

from .criteria import DSCriteria
from .criteriacomparableequal import DSCriteriaComparableEqual
from .criteriacomparablegreater import DSCriteriaComparableGreater
from .criteriacomparablegreaterorequal import DSCriteriaComparableGreaterOrEqual
from .criteriacomparablein import DSCriteriaComparableIn
from .criteriacomparableless import DSCriteriaComparableLess
from .criteriacomparablelessorequal import DSCriteriaComparableLessOrEqual
from .criteriacomparablelike import DSCriteriaComparableLike
from .criteriacomparablenotequal import DSCriteriaComparableNotEqual
from .criterialogicaland import DSCriteriaLogicalAnd
from .criterialogicalnot import DSCriteriaLogicalNot
from .criterialogicalor import DSCriteriaLogicalOr


def factory(criteria, table):
    """Convert a list and sublist into a criteria"""
    newcriteria = None
    if isinstance(criteria, DSCriteria):
        newcriteria = criteria
    elif isinstance(criteria, list):
        operator = criteria[0]
        if operator == DSCriteriaComparableEqual.SIGN:
            newcriteria = DSCriteriaComparableEqual(table[criteria[1]], criteria[2])
        elif operator == DSCriteriaComparableGreater.SIGN:
            newcriteria = DSCriteriaComparableGreater(table[criteria[1]], criteria[2])
        elif operator == DSCriteriaComparableGreaterOrEqual.SIGN:
            newcriteria = DSCriteriaComparableGreaterOrEqual(table[criteria[1]], criteria[2])
        elif operator == DSCriteriaComparableIn.SIGN:
            newcriteria = DSCriteriaComparableIn(table[criteria[1]], criteria[2])
        elif operator == DSCriteriaComparableLess.SIGN:
            newcriteria = DSCriteriaComparableLess(table[criteria[1]], criteria[2])
        elif operator == DSCriteriaComparableLessOrEqual.SIGN:
            newcriteria = DSCriteriaComparableLessOrEqual(table[criteria[1]], criteria[2])
        elif operator == DSCriteriaComparableLike.SIGN:
            newcriteria = DSCriteriaComparableLike(table[criteria[1]], criteria[2])
        elif operator == DSCriteriaComparableNotEqual.SIGN:
            newcriteria = DSCriteriaComparableNotEqual(table[criteria[1]], criteria[2])
        elif operator == DSCriteriaLogicalAnd.SIGN:
            newcriteria = DSCriteriaLogicalAnd([factory(c, table) for c in criteria[1]])
        elif operator == DSCriteriaLogicalOr.SIGN:
            newcriteria = DSCriteriaLogicalOr([factory(c, table) for c in criteria[1]])
        elif operator == DSCriteriaLogicalNot.SIGN:
            newcriteria = DSCriteriaLogicalNot([factory(c, table) for c in criteria[1]])

    return newcriteria
