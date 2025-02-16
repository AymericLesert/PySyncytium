# -*- coding: utf-8 -*-

"""
This module describes a database exception.
"""

from exception.exception import DSException

class DSExceptionDatabase(DSException):
    def __init__(self, message):
        super().__init__(message)