"""
This module handles a cursor on the database.
"""

class DSCursor:
    """This class handles a cursor on selection from the database"""

    def close(self):
        """Close and release the cursor"""
        self.__cursor.close()
        self.__cursor = None

    def __iter__(self):
        self.__iterator = iter(self.__cursor)
        return self

    def __next__(self):
        return self.__table.new(next(self.__iterator))

    def __init__(self, cursor, table):
        self.__table = table
        self.__cursor = cursor
        self.__iterator = None
