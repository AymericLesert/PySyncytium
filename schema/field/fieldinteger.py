"""
This module handles an integer field description.
"""

from .field import DSField

class DSFieldInteger(DSField):
    """
    This class handles an integer field description.
    """

    def __init__(self, fieldname, description):
        super().__init__("Integer", fieldname, description)
