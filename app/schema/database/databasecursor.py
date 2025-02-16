# -*- coding: utf-8 -*-

"""
This module handles a cursor on the database.
"""

from logger.loggerobject import DSLoggerObject

class DSDatabaseCursor(DSLoggerObject):
    """This class handles a cursor on selection from the database"""

    def close(self):
        """Close and release the cursor"""
        self.info(f"{self._nbrecords} records selected from {self.__tablename}")
        self.__cursor.close()
        self.__cursor = None

    def __iter__(self):
        self.__iterator = iter(self.__cursor)
        return self

    def __next__(self):
        try:
            record = next(self.__iterator)
        except StopIteration:
            self.close()
            raise
        for i, name in enumerate(self.__fields):
            self.__record[name] = record[i]
        self._nbrecords += 1
        return self.__record

    def __init__(self, cursor, tablename, fields):
        super().__init__()
        self.__cursor = cursor
        self.__iterator = None
        self.__tablename = tablename
        self.__fields = fields
        self.__record = {}
        for name in fields:
            self.__record[name] = None
        self._nbrecords = 0
