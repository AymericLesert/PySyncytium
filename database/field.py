"""
This module handles a field.
"""

from .criteria import DSCriteria

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
        return DSCriteria('=', self.name, value)

    def __ne__(self, value):
        return DSCriteria('<>', self.name, value)

    def __lt__(self, value):
        return DSCriteria('<', self.name, value)

    def __le__(self, value):
        return DSCriteria('<=', self.name, value)

    def __gt__(self, value):
        return DSCriteria('>', self.name, value)

    def __ge__(self, value):
        return DSCriteria('>=', self.name, value)

    def operator_in(self, *items):
        """Create a criteria on the field matching with a list of values"""
        return DSCriteria('in', self.name, items)

    def __init__(self, fieldtype, fieldname, description):
        self.__type = fieldtype
        self.__name = fieldname
        self.__description = description.get('Description', '')


class DSFieldString(DSField):
    """
    This class handles a string field description.
    """

    def to_dict(self):
        """Convert the field to a json"""
        field = super().to_dict()
        field['MaxLength'] = self.maxlength
        return field

    @property
    def maxlength(self):
        """Max lenght of the string"""
        return self.__maxlength

    def __init__(self, fieldname, description):
        super().__init__("String", fieldname, description)
        self.__maxlength = description.get('MaxLength', 256)


class DSFieldInteger(DSField):
    """
    This class handles an integer field description.
    """

    def __init__(self, fieldname, description):
        super().__init__("Integer", fieldname, description)
