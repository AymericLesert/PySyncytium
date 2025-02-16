# -*- coding: utf-8 -*-

"""
This module handles a cursor on the table.
"""

from logger.loggerobject import DSLoggerObject

class DSCursor(DSLoggerObject):
    """This class handles a cursor on selection from the database"""

    def __iter__(self):
        self.__iterator = iter(self.__cursor)
        return self

    def __next__(self):
        return self.__table.new(next(self.__iterator))

    def __init__(self, table, cursor):
        super().__init__()
        self.__cursor = cursor
        self.__iterator = None
        self.__table = table
