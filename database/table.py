"""
This module handles a table.
"""

from .field import DSFieldString, DSFieldInteger  # pylint: disable=unused-import

class DSTable:
    """
    This class handles a table description.
    """

    def to_dict(self):
        """Convert the table to a json"""
        fields = {}
        for key, value in self.__fields.items():
            fields[key] = value.to_dict()
        return {
                'Name': self.name,
                'Description': self.description,
                'Fields': fields
            }

    @property
    def name(self):
        """Name of the table"""
        return self.__name

    @property
    def description(self):
        """Description of the table"""
        return self.__description

    def where(self, clause):
        """Build a clause Where to select a list of items into the table"""
        return clause(self)

    def __getattr__(self, name):
        return self.__fields[name]

    def __init__(self, tablename, description):
        self.__name = tablename
        self.__description = description['Description']

        self.__fields = {}
        fields = description['Fields']
        for key in fields:
            # TODO: check if the fieldtype is only a word
            fieldtype = fields[key].get('Type', 'String')
            try:
                self.__fields[key] = eval(f'DSField{fieldtype}')(key, fields[key])  # pylint: disable=eval-used
            except:  # pylint: disable=bare-except
                pass
