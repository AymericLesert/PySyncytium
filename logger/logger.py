# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module handles the logger.
"""

import os
import glob
import datetime
import threading
import re
import traceback

import logging
import logging.config

from .loggertimer import DSLoggerTimer

def format_message(user, klass, module, level, message):
    """This function formats the message before writing into the log file"""
    if level is not None:
        return [f"{user} - {module}.{klass} : ({level}) {line}" for line in message.split('\n') if line.strip() != '']
    return [f"{user} - {module}.{klass} : {line}" for line in message.split('\n') if line.strip() != '']

class DSLogger:
    """This class handles a common logger for the application"""

    Instance = None

    def __writeconfiguration(self):
        """This function writes the items of the current configuration into the log file"""
        def writeconfigurationitem(root, items):
            if isinstance(items, (tuple, list)):
                for i, item in enumerate(items):
                    writeconfigurationitem(f"{root}[{i}]", item)
            elif isinstance(items, dict):
                for key, item in items.items():
                    if root == '':
                        writeconfigurationitem(key, item)
                    else:
                        writeconfigurationitem(f"{root}.{key}", item)
            else:
                self.__logger.info("%s = '%s'", root, items)

        self.__logger.info("Application : %s", self.__configuration.application)
        self.__logger.info("Version     : %s", self.__configuration.version)
        self.__logger.info("-------------------------")
        if self.isverbose:
            self.__logger.info("Verbose mode enable")
        writeconfigurationitem('', self.__configuration.items.to_dict())
        if self.__reload_timer is not None:
            self.__logger.info("Enabling reload timer (every %s seconds) ...", self.__reload_timer.interval)
        if self.__cleanup_timer is not None:
            self.__logger.info("Enabling cleanup timer (every %s seconds) ...", self.__cleanup_timer.interval)

    @property
    def isverbose(self):
        """Indicates if the log file is verbose mode"""
        return self.__debug and self.__verbose

    @property
    def isdebug(self):
        """Indicates if the log file is debug mode"""
        return self.__debug

    def open(self):
        """This function opens the current and writes some common informations"""
        self.__logger.info("----------------------------------------------")
        self.__writeconfiguration()
        if self.__reload_timer is not None:
            self.__reload_timer.start()
        if self.__cleanup_timer is not None:
            self.__cleanup_timer.start()

    def reload(self):
        """
        This function reloads the configuration and check if one of the handler file has a new filename.
        In this case, the configuration is reloaded, the previous file is closed and the new file is opened
        """
        with self.__lock:
            self.__logger.debug("(V) Checking a new configuration ...")
            try:
                change = False

                for handler in self.__logger.handlers:
                    if isinstance(handler, logging.FileHandler):
                        if not handler.name in self.__files:
                            continue

                        newfilename = self.__configuration.items.logging.handlers[handler.name].filename
                        if newfilename != self.__files[handler.name]:
                            change = True
                            break

                if change:
                    self.__logger.info("Reloading configuration due to a new filename ...")
                    self.__logger.info("----------------------------------------------")

                    logging.config.dictConfig(self.__configuration.items.logging.to_dict())
                    self.__logger.info("----------------------------------------------")
                    self.__writeconfiguration()
            except:
                pass

    def cleanup(self):
        """
        This function cleans up the file of log files and removes all files older than a given date
        """
        with self.__lock:
            self.__logger.debug("(V) Cleaning up files ...")
            try:
                limitdate = datetime.datetime.now() + \
                            datetime.timedelta(seconds=-self.__configuration.items.logging.cleanup.nbdays * 86400)
                pattern = re.compile(self.__configuration.items.logging.cleanup.pattern)
                self.__logger.info("Cleaning up older file than %s ...", limitdate.strftime("%Y-%m-%d %H:%M:%S"))
                for file in glob.glob(os.path.join(os.getcwd(), self.__configuration.items.logging.cleanup.directory, '*')):
                    update_file = datetime.datetime.fromtimestamp(os.path.getmtime(file))
                    if update_file <= limitdate and pattern.match(os.path.basename(file)):
                        self.__logger.info("Removing file %s ...", file)
                        os.remove(file)
            except:
                pass

    def close(self):
        """This function closes the current log files"""
        if self.__reload_timer is not None:
            self.__logger.info("Stop reload timer ...")
            self.__reload_timer.stop()
        if self.__cleanup_timer is not None:
            self.__logger.info("Stop clean up timer ...")
            self.__cleanup_timer.stop()
        self.__logger.info("Close the log file")
        self.__logger.info("----------------------------------------------")

    def verbose(self, user, klass, module, message):
        """This function traces a verbose message into the log file"""
        if self.isverbose:
            return
        with self.__lock:
            try:
                for line in format_message(user, klass, module, "V", message):
                    self.__logger.debug(line)
            except:
                pass

    def debug(self, user, klass, module, message):
        """This function traces a debug message into the log file"""
        with self.__lock:
            try:
                for line in format_message(user, klass, module, None, message):
                    self.__logger.debug(line)
            except:
                pass

    def info(self, user, klass, module, message):
        """This function traces an info message into the log file"""
        with self.__lock:
            try:
                for line in format_message(user, klass, module, None, message):
                    self.__logger.info(line)
            except:
                pass

    def warning(self, user, klass, module, message):
        """This function traces a warning message into the log file"""
        with self.__lock:
            try:
                for line in format_message(user, klass, module, None, message):
                    self.__logger.warning(line)
            except:
                pass

    def error(self, user, klass, module, message):
        """This function traces an error message into the log file"""
        with self.__lock:
            try:
                for line in format_message(user, klass, module, None, message):
                    self.__logger.error(line)
            except:
                pass

    def critical(self, user, klass, module, message):
        """This function traces a critical message into the log file"""
        with self.__lock:
            try:
                for line in format_message(user, klass, module, None, message):
                    self.__logger.critical(line)
            except:
                pass

    def exception(self, user, klass, module, message):
        """This function traces the current exception raised into the log file"""
        with self.__lock:
            try:
                for line in format_message(user, klass, module, None, message):
                    self.__logger.error(line)
                for line in format_message(user, klass, module, None, traceback.format_exc()):
                    self.__logger.error(line)
            except:
                pass

    def __init__(self, configuration):
        logging.config.dictConfig(configuration.items.logging.to_dict())

        self.__configuration = configuration
        self.__logger = logging.getLogger()
        self.__lock = threading.Lock()
        self.__reload_timer = None
        self.__cleanup_timer = None
        self.__debug = False
        self.__verbose = self.__configuration.items.get_property('logging.verbose', False)
        self.__files = {}

        for handler in self.__logger.handlers:
            if self.__configuration.get_property(f"logging.handlers.{handler.name}.level", "INFO") == "DEBUG":
                self.__debug = True
            if isinstance(handler, logging.FileHandler):
                self.__files[handler.name] = self.__configuration.items.logging.handlers[handler.name].filename

        interval = self.__configuration.items.get_property('logging.reload.interval', None)
        if interval is not None:
            self.__reload_timer = DSLoggerTimer(self.reload, interval)

        interval = self.__configuration.items.get_property('logging.cleanup.interval', None)
        if interval is not None:
            self.__cleanup_timer = DSLoggerTimer(self.cleanup, interval)
        self.__class__.Instance = self
