"""
This module handles an abstract field.
"""

from ..criteria.criteriacomparableequal import DSCriteriaComparableEqual
from ..criteria.criteriacomparablenotequal import DSCriteriaComparableNotEqual
from ..criteria.criteriacomparableless import DSCriteriaComparableLess
from ..criteria.criteriacomparablelessorequal import DSCriteriaComparableLessOrEqual
from ..criteria.criteriacomparablegreater import DSCriteriaComparableGreater
from ..criteria.criteriacomparablegreaterorequal import DSCriteriaComparableGreaterOrEqual
from ..criteria.criteriacomparablein import DSCriteriaComparableIn
from ..criteria.criteriacomparablelike import DSCriteriaComparableLike

class DSField:
    """
    This class handles a field description.
    """

    def to_dict(self):
        """Convert the field to a json"""
        return {
                'Name': self.name,
                'Type': self.type,
                'Description': self.description
            }

    @property
    def type(self):
        """Type of the field"""
        return self.__type

    @property
    def name(self):
        """Name of the field"""
        return self.__name

    @property
    def description(self):
        """Description of the field"""
        return self.__description

    def __eq__(self, value):
        return DSCriteriaComparableEqual(self, value)

    def __ne__(self, value):
        return DSCriteriaComparableNotEqual(self, value)

    def __lt__(self, value):
        return DSCriteriaComparableLess(self, value)

    def __le__(self, value):
        return DSCriteriaComparableLessOrEqual(self, value)

    def __gt__(self, value):
        return DSCriteriaComparableGreater(self, value)

    def __ge__(self, value):
        return DSCriteriaComparableGreaterOrEqual(self, value)

    def operator_in(self, *items):
        """Create a criteria on the field matching with a list of values"""
        return DSCriteriaComparableIn(self, items)

    def operator_like(self, value):
        """Create a criteria on the field matching with a value corresponding to the like SQL"""
        return DSCriteriaComparableLike(self, value)

    def __init__(self, fieldtype, fieldname, description):
        self.__type = fieldtype
        self.__name = fieldname
        self.__description = description.get('Description', '')
