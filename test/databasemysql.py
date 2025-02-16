# -*- coding: utf-8 -*-

"""
Unit test (Database MySQL)
"""

import unittest
import os
from dotenv import load_dotenv

from configuration.configuration import DSConfiguration
from logger.logger import DSLogger

from app.schema.database.databasemysql import DSDatabaseMySQL

class TestDSDatabaseMySQL(unittest.TestCase):
    """This class tests the mysql connection behavior"""

    def test_connection(self):
        """Checks if the connection can be done"""
        with DSDatabaseMySQL(os.getenv("ROOT_DATABASE_HOSTNAME", "localhost"),
                             os.getenv("ROOT_DATABASE_USERNAME"),
                             os.getenv("ROOT_DATABASE_PASSWORD"),
                             "Syncytium") as db:
            _ = db.schema

if __name__ == "__main__":
    load_dotenv()
    configuration = DSConfiguration('config.yml')
    log = DSLogger(configuration)
    log.open()
    unittest.main()
    log.close()
