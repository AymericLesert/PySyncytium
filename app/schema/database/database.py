# -*- coding: utf-8 -*-

"""
This module handles the database connexion.
"""

# pylint: disable=unused-argument

class DSDatabase:
    """This abstract class describes the main functions from a database connexion"""

    def connect(self):
        """This abstract method describes the connection to the database"""
        return self

    @property
    def is_connected(self):
        """Return if the connection is done"""
        return False

    def get_description(self, schema):
        """Retrieve a JSON description of the tables from a given schema"""
        return {}

    def begin_transaction(self):
        """Start a new transaction"""
        return self

    def insert(self, dstable, values):
        """Return the list of keys created while inserting the list of values"""
        return None

    def select(self, dstable, clause):
        """Return a cursor to the selection of the dstable"""
        return None

    def update(self, dstable, oldvalue, newvalue):
        """Return the key updated"""
        return None

    def delete(self, dstable, values):
        """Return the list of keys removed"""
        return None

    def end_transaction(self):
        """Close the current transaction"""
        return self

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
