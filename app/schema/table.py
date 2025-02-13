# -*- coding: utf-8 -*-

"""
This module handles a table.
"""

from .record import DSRecord

from .field.fieldstring import DSFieldString # pylint: disable=unused-import
from .field.fieldinteger import DSFieldInteger  # pylint: disable=unused-import

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
                'Fields': fields,
                'Key': self.key
            }

    @property
    def name(self):
        """Name of the table"""
        return self.__name

    @property
    def description(self):
        """Description of the table"""
        return self.__description

    @property
    def key(self):
        """Name of the field key of the table"""
        return self.__key

    @property
    def fields(self):
        """List of field name"""
        return list(self.__fields.keys())

    @property
    def schema(self):
        """Reference on the schema of the table"""
        return self.__schema

    def new(self, value = None):
        """Retrieve a new record from the current table"""
        record = DSRecord(self)
        if isinstance(value, tuple):
            for index, fieldname in enumerate(self.__fields):
                record[fieldname] = value[index]
        elif isinstance(value, dict):
            for fieldname in self.__fields:
                if fieldname in value:
                    record[fieldname] = value[fieldname]

        return record

    def insert(self, values):
        """Insert one or many records into the database"""
        keys = self.__schema.database.insert(self, values)
        if isinstance(values, list):
            for key, value in zip(keys, values):
                value[self.key] = key
        else:
            values[self.key] = keys[0]
        return values

    def select(self, clause):
        """Retrieve the list of records matching within the clause"""
        return self.__schema.database.select(self, clause(self))

    def update(self, oldvalue, newvalue):
        """Update a record into the database"""
        newkeyupdated = self.__schema.database.update(self, oldvalue, newvalue)
        if newkeyupdated is None:
            return None
        return newvalue

    def delete(self, values):
        """Delete one or many records into the database"""
        keys = self.__schema.database.delete(self, values)
        if isinstance(values, list):
            for key, value in zip(keys, values):
                value[self.key] = key
        else:
            values[self.key] = keys[0]
        return values

    def __getattr__(self, name):
        return self.__fields[name]

    def __getitem__(self, name):
        return self.__fields[name]

    def __iter__(self):
        if self.__select is not None:
            return self
        self.__select = self.__schema.database.select(self)
        self.__iterator_select = iter(self.__select)
        # return self.__iterator_select
        return self

    def __next__(self):
        try:
            return next(self.__iterator_select)
        except StopIteration as e:
            self.__select.close()
            self.__select = None
            self.__iterator_select = None
            raise e

    def __init__(self, schema, tablename, description):
        self.__schema = schema
        self.__name = tablename
        self.__description = description['Description']
        self.__key = description['Key']

        self.__select = None
        self.__iterator_select = None

        self.__fields = {}
        fields = description['Fields']
        for key in fields:
            # TODO: check if the fieldtype is only a word
            fieldtype = fields[key].get('Type', 'String')
            try:
                self.__fields[key] = eval(f'DSField{fieldtype}')(self, key, fields[key])  # pylint: disable=eval-used
            except:  # pylint: disable=bare-except
                pass
