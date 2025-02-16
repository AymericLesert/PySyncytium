# -*- coding: utf-8 -*-

"""
This module describes a database not connected exception.
"""

from exception.exceptiondatabase import DSExceptionDatabase

class DSExceptionDatabaseNotConnected(DSExceptionDatabase):
    def __init__(self, message):
        super().__init__(message)