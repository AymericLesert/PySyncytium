# -*- coding: utf-8 -*-

"""
This module describes an exception for the application.
"""

class DSException(Exception):
    def __init__(self, message):
        super().__init__(message)