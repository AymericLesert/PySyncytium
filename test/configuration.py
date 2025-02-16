# -*- coding: utf-8 -*-

"""
Unit test (Configuration)
"""

import unittest
import datetime
from dotenv import load_dotenv

from configuration.configuration import DSConfiguration

class TestDSConfiguration(unittest.TestCase):
    """This class tests the configuration behavior"""

    def setUp(self):
        """Initialization of the configuration items"""
        self.configuration = DSConfiguration('test/configuration.yml')

    def test_json(self):
        """Checks if the dictionaries are expected (from the file and from the interpretation)"""
        self.assertEqual(self.configuration.to_dict(),
                         {
                             "name": "Test unitaire", 
                             "logging": 
                             {
                                 "version": 1, 
                                 "verbose": True, 
                                 "syncytium": {
                                     "reload": {
                                         "interval": 60
                                         },
                                     "cleanup": {
                                         "interval": 86400,
                                         "directory": "${SYNCYTIUM_LOG_DIRECTORY}",
                                         "pattern": "^${APPLICATION}-.*\\.log$",
                                         "nbdays": 20
                                         },
                                     "loggers": ["fastapi", "uvicorn"]
                                     },
                                 "formatters": {
                                     "standard": {
                                         "format": "%(asctime)s [%(levelname)-5s] (%(process)d:%(processName)s) %(message)s"
                                         }
                                     },
                                 "handlers": {
                                     "console": {
                                         "class": "logging.StreamHandler",
                                         "level": "INFO",
                                         "formatter": "standard",
                                         "stream": "ext://sys.stdout"
                                         },
                                     "file": {
                                         "class": "logging.handlers.RotatingFileHandler",
                                         "level": "DEBUG",
                                         "formatter": "standard",
                                         "filename": "${SYNCYTIUM_LOG_DIRECTORY}/${APPLICATION}-${date:%Y-%m-%d}.log",
                                         "maxBytes": 16777216,
                                         "backupCount": 10,
                                         "encoding": "utf8"
                                         }
                                     },
                                 "root": {
                                     "level": "NOTSET",
                                     "handlers": ["console", "file"]
                                     }
                                 },
                                 "database": {
                                     "hostname": "localhost",
                                     "username": "${DATABASE_USERNAME}",
                                     "password*": "${DATABASE_PASSWORD}",
                                     "basename": ["DEV", "UAT", "PROD"],
                                     "essai": "${hostname}/${.database.username}:${basename[1]}"
                                     }
                                 })
        self.assertEqual(self.configuration.items.to_dict(),
                         {
                             "name": "Test unitaire",
                             "logging":
                             {
                                 "version": 1,
                                 "verbose": True,
                                 "syncytium": {
                                     "reload": {
                                         "interval": 60
                                         },
                                     "cleanup": {
                                         "interval": 86400,
                                         "directory": "logs",
                                         "pattern": "^" + self.configuration.application + "-.*\\.log$",
                                         "nbdays": 20
                                         },
                                     "loggers": ["fastapi", "uvicorn"]
                                     },
                                 "formatters": {
                                     "standard": {
                                         "format": "%(asctime)s [%(levelname)-5s] (%(process)d:%(processName)s) %(message)s"
                                         }
                                     },
                                 "handlers": {
                                     "console": {
                                         "class": "logging.StreamHandler",
                                         "level": "INFO",
                                         "formatter": "standard",
                                         "stream": "ext://sys.stdout"
                                         },
                                     "file": {
                                         "class": "logging.handlers.RotatingFileHandler",
                                         "level": "DEBUG",
                                         "formatter": "standard",
                                         "filename": "logs/" +
                                                        self.configuration.application +
                                                        "-" +
                                                        datetime.datetime.now().strftime("%Y-%m-%d") +
                                                        ".log",
                                         "maxBytes": 16777216,
                                         "backupCount": 10,
                                         "encoding": "utf8"
                                         }
                                     },
                                 "root": {
                                     "level": "NOTSET",
                                     "handlers": ["console", "file"]
                                     }
                                 },
                                 "database": {
                                     "hostname": "localhost",
                                     "username": "root",
                                     "basename": ["DEV", "UAT", "PROD"],
                                     "essai": "localhost/root:UAT"
                                     }
                                 })

    def test_values(self):
        """Checks if values returned are expected"""
        self.assertEqual(self.configuration.items.logging.formatters.standard.format,
                         "%(asctime)s [%(levelname)-5s] (%(process)d:%(processName)s) %(message)s")
        self.assertEqual(self.configuration.items.database.hostname, "localhost")
        self.assertEqual(self.configuration.items.database.username, "root")
        self.assertEqual(self.configuration.get("database.username", None), "root")
        self.assertEqual(self.configuration.get("database.unknown", "#NA"), "#NA")
        self.assertEqual(self.configuration.application, "Syncytium")
        self.assertRegex(self.configuration.version, r"^v[0-9]+(\.[0-9]+)*$")
        with self.assertRaises(KeyError):
            _ = self.configuration.items.database.unknown

if __name__ == "__main__":
    load_dotenv()
    unittest.main()
