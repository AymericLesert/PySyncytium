"""
This module handles a select criteria.
"""

class DSCriteria:
    """
    This class handles a field description.
    """

    @property
    def criteria(self):
        """Get a tuple describing the criteria details"""
        return self.__criteria

    def __str__(self):
        return str(self.__criteria)

    def operator_and(self, *items):
        """Define a boolean expression within 'and'"""
        criterias = ['and', self.__criteria]
        for item in items:
            criterias.append(item.criteria)
        self.__criteria = tuple(criterias)
        return self

    def __and__(self, item):
        """Define a boolean expression overriding '&'"""
        self.__criteria = ('and', self.__criteria, item.criteria)
        return self

    def operator_or(self, *items):
        """Define a boolean expression within 'or'"""
        criterias = ['or', self.__criteria]
        for item in items:
            criterias.append(item.criteria)
        self.__criteria = tuple(criterias)
        return self

    def __or__(self, item):
        """Define a boolean expression overriding '|'"""
        self.__criteria = ('or', self.__criteria, item.criteria)
        return self

    def operator_not(self):
        """Define a boolean expression overriding 'not'"""
        self.__criteria = ('not', self.__criteria)
        return self

    def __init__(self, comparable, fieldname, value):
        self.__criteria = (comparable, fieldname, value)
