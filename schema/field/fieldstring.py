"""
This module handles a string field description.
"""

from .field import DSField

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

    def __init__(self, table, fieldname, description):
        super().__init__(table, "String", fieldname, description)
        self.__maxlength = description.get('MaxLength', 256)
