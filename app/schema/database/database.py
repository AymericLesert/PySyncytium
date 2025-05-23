# -*- coding: utf-8 -*-
# pylint: disable=unused-argument

"""
This module handles the database connexion.
"""

from logger.loggerobject import DSLoggerObject

class DSDatabase(DSLoggerObject):
    """This abstract class describes the main functions from a database connexion"""

    def to_dict(self):
        """Retrieves the database instance into a dictionary"""
        return {}

    def connect(self):
        """This abstract method describes the connection to the database"""
        return self

    @property
    def isconnected(self):
        """Return if the connection is done"""
        return False

    @property
    def schema(self):
        """Retrieve a JSON description of the tables from a given schema"""
        return {}

    def migrate(self, schema, database, allprivileges):
        """Create or upgrade a schema from the json description"""
        return False

    def insert(self, tablename, fields, values):
        """Return the list of values inserted into a table"""
        return None

    def select(self, tablename, fields, clause = None):
        """Return a cursor to the selection of the dstable"""
        return None

    def update(self, tablename, fields, oldvalues, newvalues):
        """Return the new value"""
        return None

    def delete(self, tablename, fields, values):
        """Return the list of values removed"""
        return None

    def commit(self):
        """Commit the current transaction"""
        return self

    def rollback(self):
        """Rollback the current transaction"""
        return self

    def disconnect(self):
        """This abstract method describes the disconnection to the database"""
        return self

    def __enter__(self):
        return self.connect()

    def __exit__(self, *args):
        self.disconnect()
