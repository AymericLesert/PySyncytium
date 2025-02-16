# -*- coding: utf-8 -*-

"""
This module handles a schema.
"""

from logger.loggerobject import DSLoggerObject
from .table import DSTable

class DSSchema(DSLoggerObject):
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
    def isconnected(self):
        """Return if the connection is done"""
        return self.__database.isconnected

    @property
    def database(self):
        """Return the current database session"""
        return self.__database

    def set_user(self, user):
        """Set the current user name (to trace information into the log file)"""
        super().set_user(user)
        self.__database.set_user(user)
        for table in self.__tables.values():
            table.set_user(user)
        return self

    def commit(self):
        """Commit current transaction"""
        self.verbose("Committing transaction ...")
        self.__database.commit()

    def rollback(self):
        """Rollback current transaction"""
        self.verbose("Rollbacking transaction ...")
        self.__database.rollback()

    def __getattr__(self, name):
        return self.__tables[name]

    def __getitem__(self, name):
        return self.__tables[name]

    def __enter__(self):
        return self.__database.__enter__()

    def __exit__(self, *args):
        self.__database.__exit__()

    def __init__(self, database, schema):
        self.__name = schema['Name']
        self.__description = schema.get('Description', '')
        self.__tables = {}
        self.__database = database

        tables = schema.get('Tables', {})
        for key in tables.keys():
            self.__tables[key] = DSTable(self, key, tables[key])
