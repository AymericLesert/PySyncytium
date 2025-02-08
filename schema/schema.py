# -*- coding: utf-8 -*-

"""
This module handles a schema.
"""

from .table import DSTable

class DSSchema:
    """
    This class handles an instance of a current database schema.
    """

    def to_dict(self):
        """Convert the schema to a json"""
        tables = {}
        for key, value in self.__tables.items():
            tables[key] = value.to_dict()
        return {
                'Name': self.name,
                'Description': self.description,
                'Tables': tables
            }

    @property
    def name(self):
        """Name of the schema"""
        return self.__name

    @property
    def description(self):
        """Description of the schema"""
        return self.__description

    @property
    def tables(self):
        """List of table name"""
        return list(self.__tables.keys())

    @property
    def database(self):
        """Retrieve the instance of the database connection"""
        return self.__db

    @database.setter
    def database(self, value):
        """Set the instance of the current database connection"""
        self.__db = value

    def __getattr__(self, name):
        return self.__tables[name]

    def __getitem__(self, name):
        return self.__tables[name]

    def __init__(self, schema):
        self.__name = schema['Name']
        self.__description = schema.get('Description', '')
        self.__tables = {}
        self.__db = None

        tables = schema.get('Tables', {})
        for key in tables:
            self.__tables[key] = DSTable(self, key, tables[key])
