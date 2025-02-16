# -*- coding: utf-8 -*-

"""
This module handles a table.
"""

from logger.loggerobject import DSLoggerObject

from .record import DSRecord
from .cursor import DSCursor

from .field.fieldstring import DSFieldString # pylint: disable=unused-import
from .field.fieldinteger import DSFieldInteger  # pylint: disable=unused-import

class DSTable(DSLoggerObject):
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
        """Create a new record from the current table"""
        record = DSRecord(self)
        if isinstance(value, (list, tuple)):
            for index, fieldname in enumerate(self.__fields):
                record[fieldname] = value[index]
        elif isinstance(value, dict):
            for fieldname in self.__fields:
                if fieldname in value:
                    record[fieldname] = value[fieldname]

        return record

    def insert(self, values):
        """Insert one or many records into the database"""
        if self.isverbose:
            if isinstance(values, (tuple, list)):
                self.verbose(f"Inserting {len(values)} records into the table '{self.__schema.name}.{self.name}' ...")
            else:
                self.verbose(f"Inserting a record into the table '{self.__schema.name}.{self.name}' ...")
        return self.__schema.database.insert(self.name, self.fields, values)

    def select(self, clause = None):
        """Retrieve a cursor on the list of records matching within the clause"""
        where = None
        if clause is not None:
            if isinstance(clause, str):
                where = clause
            else:
                where = clause(self)
        self.verbose(f"Selecting values from the table '{self.__schema.name}.{self.name}' ...")
        return DSCursor(self, self.__schema.database.select(self.name, self.fields, where)).set_user(self.user)

    def update(self, oldvalues, newvalues):
        """Update one or many records into the database"""
        if self.isverbose:
            if isinstance(oldvalues, (tuple, list)):
                self.verbose(f"Updating {len(oldvalues)} records into the table '{self.__schema.name}.{self.name}' ...")
            else:
                self.verbose(f"Updating a record into the table '{self.__schema.name}.{self.name}' ...")
        return self.__schema.database.update(self.name, self.fields, oldvalues, newvalues)

    def delete(self, values):
        """Delete one or many records into the database"""
        if self.isverbose:
            if isinstance(values, (tuple, list)):
                self.verbose(f"Deleting {len(values)} records into the table '{self.__schema.name}.{self.name}' ...")
            else:
                self.verbose(f"Deleting a record into the table '{self.__schema.name}.{self.name}' ...")
        return self.__schema.database.delete(self.name, self.fields, values)

    def __getattr__(self, name):
        return self.__fields[name]

    def __getitem__(self, name):
        return self.__fields[name]

    def __iter__(self):
        if self.__cursor is not None:
            self.__cursor.close()
            self.__cursor = None
            self.__iterator = None

        self.__cursor = DSCursor(self, self.__schema.database.select(self.name, self.fields)).set_user(self.user)
        self.__iterator = iter(self.__cursor)
        return self

    def __next__(self):
        try:
            return next(self.__iterator)
        except StopIteration:
            self.__cursor = None
            self.__iterator = None
            raise

    def __init__(self, schema, tablename, description):
        super().__init__()
        self.__schema = schema
        self.__name = tablename
        self.__description = description['Description']
        self.__key = description['Key']

        self.__cursor = None
        self.__iterator = None

        self.__fields = {}
        fields = description['Fields']
        for key in fields.keys():
            # TODO: check if the fieldtype is only a word (use a factory)
            fieldtype = fields[key].get('Type', 'String')
            try:
                self.__fields[key] = eval(f'DSField{fieldtype}')(self, key, fields[key])  # pylint: disable=eval-used
            except:  # pylint: disable=bare-except
                pass
