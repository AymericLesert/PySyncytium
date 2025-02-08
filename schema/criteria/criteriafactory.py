# -*- coding: utf-8 -*-

"""Create a criteria from a dictionary"""

from schema.criteria.criteria import DSCriteria
from schema.criteria.criteriacomparableequal import DSCriteriaComparableEqual
from schema.criteria.criteriacomparablegreater import DSCriteriaComparableGreater
from schema.criteria.criteriacomparablegreaterorequal import DSCriteriaComparableGreaterOrEqual
from schema.criteria.criteriacomparablein import DSCriteriaComparableIn
from schema.criteria.criteriacomparableless import DSCriteriaComparableLess
from schema.criteria.criteriacomparablelessorequal import DSCriteriaComparableLessOrEqual
from schema.criteria.criteriacomparablelike import DSCriteriaComparableLike
from schema.criteria.criteriacomparablenotequal import DSCriteriaComparableNotEqual
from schema.criteria.criterialogicaland import DSCriteriaLogicalAnd
from schema.criteria.criterialogicalnot import DSCriteriaLogicalNot
from schema.criteria.criterialogicalor import DSCriteriaLogicalOr


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
