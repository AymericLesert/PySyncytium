# -*- coding: utf-8 -*-

"""
This module handles a generic record from a table.
"""

class DSRecord:
    """This class describes a generic record from any table"""

    def to_dict(self):
        """Convert the record to a dict"""
        record = {}
        for fieldname in self.table.fields:
            record[fieldname] = self[fieldname]
        return record

    @property
    def table(self):
        """Retrieve the table attached to this record"""
        return self.__table

    def clone(self):
        """Clone the current instance of record"""
        record = DSRecord(self.table)
        for fieldname in self.table.fields:
            record[fieldname] = self[fieldname]
        return record

    def __eq__(self, record):
        if self.table != record.table:
            return False
        for fieldname in self.table.fields:
            if record[fieldname] != self[fieldname]:
                return False
        return True

    def __str__(self):
        return "{" + ", ".join([f"{fieldname}={self.__fields[fieldname][1]}"
                                for fieldname in self.__fields]) + "}"

    def __getattr__(self, fieldname):
        if fieldname in self.__fields:
            return self.__fields[fieldname][1]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{fieldname}'")

    def __getitem__(self, fieldname):
        if fieldname in self.__fields:
            return self.__fields[fieldname][1]
        raise KeyError(f"Field '{fieldname}' not found in record.")

    def __setattr__(self, fieldname, value):
        if fieldname in self.__dict__["_DSRecord__fields"]:
            self.__fields[fieldname][1] = value
        else:
            super().__setattr__(fieldname, value)

    def __setitem__(self, fieldname, value):
        if fieldname in self.__fields:
            self.__fields[fieldname][1] = value
        else:
            raise KeyError(f"Field '{fieldname}' not found in record.")

    def __init__(self, dstable):
        self.__dict__["_DSRecord__table"] = dstable
        self.__dict__["_DSRecord__fields"] = {}
        for fieldname in dstable.fields:
            self.__fields[fieldname] = [dstable[fieldname], dstable[fieldname].defaultvalue]
