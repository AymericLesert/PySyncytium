# -*- coding: utf-8 -*-

"""
This module describes an abstract class of logger item.
"""

import os
import time
import getpass
from functools import wraps

from .logger import DSLogger

class DSLoggerObject:
    """Base object describing logger functions"""

    @property
    def isverbose(self):
        """Indicates if the log file is verbose mode"""
        if DSLogger.Instance:
            return DSLogger.Instance.isverbose
        return False

    @property
    def isdebug(self):
        """Indicates if the log file is debug mode"""
        if DSLogger.Instance:
            return DSLogger.Instance.isdebug
        return False

    def verbose(self, message, user = os.getlogin()):
        """This function traces a verbose message into the log file"""
        if DSLogger.Instance:
            DSLogger.Instance.verbose(user, self.__class__.__name__, __name__, message)

    def debug(self, message, user = os.getlogin()):
        """This function traces a debug message into the log file"""
        if DSLogger.Instance:
            DSLogger.Instance.debug(user, self.__class__.__name__, __name__, message)

    def info(self, message, user = os.getlogin()):
        """This function traces an info message into the log file"""
        if DSLogger.Instance:
            DSLogger.Instance.info(user, self.__class__.__name__, __name__, message)

    def warning(self, message, user = os.getlogin()):
        """This function traces a warning message into the log file"""
        if DSLogger.Instance:
            DSLogger.Instance.warning(user, self.__class__.__name__, __name__, message)

    def error(self, message, user = os.getlogin()):
        """This function traces an error message into the log file"""
        if DSLogger.Instance:
            DSLogger.Instance.error(user, self.__class__.__name__, __name__, message)

    def critical(self, message, user = os.getlogin()):
        """This function traces a critical message into the log file"""
        if DSLogger.Instance:
            DSLogger.Instance.critical(user, self.__class__.__name__, __name__, message)

    def exception(self, message, user = os.getlogin()):
        """This function traces the current exception raised into the log file"""
        if DSLogger.Instance:
            DSLogger.Instance.exception(user, self.__class__.__name__, __name__, message)


def asyncloggerexecutiontime(func):
    """Trace the function calling and execution time"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        username = kwargs.get("user", None)
        if username:
            username = username['sub']
        else:
            try:
                username = os.getlogin()
            except OSError:
                username = getpass.getuser()

        if DSLogger.Instance:
            DSLogger.Instance.debug(username, func.__name__, __name__, "Starting ...")

        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time

        if DSLogger.Instance:
            DSLogger.Instance.info(username, func.__name__, __name__, f"Execution in {execution_time:.4f} seconds")
        return result
    return wrapper
