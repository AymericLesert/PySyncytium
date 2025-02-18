# -*- coding: utf-8 -*-
# pylint: disable=bare-except

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

    def test_01_connection(self):
        """Checks if the connection can be done"""
        with DSDatabaseMySQL(os.getenv("PSTEST_DATABASE_HOSTNAME", "localhost"),
                             os.getenv("PSTEST_DATABASE_USERNAME"),
                             os.getenv("PSTEST_DATABASE_PASSWORD"),
                             "PSTest"):
            pass

    def test_02_schema(self):
        """Retrieves the schema from database"""
        with DSDatabaseMySQL(os.getenv("PSTEST_DATABASE_HOSTNAME", "localhost"),
                             os.getenv("PSTEST_DATABASE_USERNAME"),
                             os.getenv("PSTEST_DATABASE_PASSWORD"),
                             "PSTest") as db:
            _ = db.schema

    def test_03_select(self):
        """Test select instruction"""
        with DSDatabaseMySQL(os.getenv("PSTEST_DATABASE_HOSTNAME", "localhost"),
                             os.getenv("PSTEST_DATABASE_USERNAME"),
                             os.getenv("PSTEST_DATABASE_PASSWORD"),
                             "PSTest") as db:
            for record in db.select("User", ["Name", "Age"]):
                print(record)

            for record in db.select("User", ["Name", "Age"], "`Name` in ('Aymeric', 'Marie')"):
                print(record)

    def test_04_insert(self):
        """Test insert instruction"""
        with DSDatabaseMySQL(os.getenv("PSTEST_DATABASE_HOSTNAME", "localhost"),
                             os.getenv("PSTEST_DATABASE_USERNAME"),
                             os.getenv("PSTEST_DATABASE_PASSWORD"),
                             "PSTest") as db:
            try:
                db.insert("User", ["Name", "Age", "PhoneNumber"], [{"Name": "Tutu", "Age": 32, "PhoneNumber": "Test"}])
                db.commit()
            except:
                db.rollback()
            for record in db.select("User", ["Name", "Age", "PhoneNumber"]):
                print(record)

    def test_05_update(self):
        """Test update instruction"""
        with DSDatabaseMySQL(os.getenv("PSTEST_DATABASE_HOSTNAME", "localhost"),
                             os.getenv("PSTEST_DATABASE_USERNAME"),
                             os.getenv("PSTEST_DATABASE_PASSWORD"),
                             "PSTest") as db:
            try:
                db.update("User", ["Name", "Age", "PhoneNumber"],
                          {"Name": "Tutu", "Age": 32, "PhoneNumber": "Test"},
                          {"Name": "Titi", "Age": 77, "PhoneNumber": "Mobile"})
                db.rollback()
            except:
                db.rollback()

            try:
                db.update("User", ["Name", "Age", "PhoneNumber"],
                          [{"Name": "Tutu", "Age": 32, "PhoneNumber": "Test"},
                           {"Name": "Aymeric", "Age": 24, "PhoneNumber": "06.83.34.04.93"}],
                          [{"Name": "Titi", "Age": 77, "PhoneNumber": "Mobile"},
                           {"Name": "Aymeric", "Age": 24, "PhoneNumber": "06.83.34.04.93"}])
                db.commit()
            except:
                db.rollback()

            for record in db.select("User", ["Name", "Age", "PhoneNumber"]):
                print(record)

    def test_06_delete(self):
        """Test delete instruction"""
        with DSDatabaseMySQL(os.getenv("PSTEST_DATABASE_HOSTNAME", "localhost"),
                             os.getenv("PSTEST_DATABASE_USERNAME"),
                             os.getenv("PSTEST_DATABASE_PASSWORD"),
                             "PSTest") as db:
            try:
                db.delete("User", ["Name"], [{"Name": "Tutu"}, {"Name": "Titi"}])
                db.commit()
            except:
                db.rollback()

            for record in db.select("User", ["Name", "Age", "PhoneNumber"]):
                print(record)

if __name__ == "__main__":
    load_dotenv()
    log = DSLogger(DSConfiguration('test/database.yml'))
    log.open()
    unittest.main()
    log.close()
