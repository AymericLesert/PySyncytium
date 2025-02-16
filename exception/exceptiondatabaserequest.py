# -*- coding: utf-8 -*-

"""
This module describes a database exception on executing request.
"""

from exception.exceptiondatabase import DSExceptionDatabase

class DSExceptionDatabaseRequest(DSExceptionDatabase):
    def __init__(self, message):
        super().__init__(message)