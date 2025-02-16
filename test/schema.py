# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
Unit test (Schema)
"""

import unittest
from dotenv import load_dotenv

from configuration.configuration import DSConfiguration
from logger.logger import DSLogger

from app.schema.database.databasefactory import factory as databasefactory
from app.schema.schema import DSSchema

configuration = {
    "items": {
        "database": {},
        "schema": {}
        }
    }

class TestDSSchema(unittest.TestCase):
    """This class tests the schema behavior"""
    def setUp(self):
        self.schema = DSSchema(databasefactory(configuration.items.database), configuration.items.schema).set_user("Test")

    def test_01_connection(self):
        """Checks if the schema is read and the connection can be done"""
        with self.schema:
            pass

    def test_02_select(self):
        """Select a list of records"""
        with self.schema:
            for record in self.schema.User:
                print(record)

            for record in self.schema.User.select(lambda user: user.Name.in_('Aymeric', 'Marie')):
                print(record)

    def test_03_insert(self):
        """Insert a list of records"""
        with self.schema:
            usertiti = self.schema.User.new()
            usertiti.Name = "Titi"
            usertiti.Age = 99
            usertiti.PhoneNumber = "99.99.99.99.99"
            self.schema.User.insert(usertiti)

            for record in self.schema.User:
                print(record)

            usertutu1 = self.schema.User.new()
            usertutu1.Name = "Tutu-1"
            usertutu1.Age = 15
            usertutu1.PhoneNumber = "08.08.99.99.99"

            usertutu2 = self.schema.User.new()
            usertutu2.Name = "Tutu-2"
            usertutu2.Age = 51
            usertutu2.PhoneNumber = "06.06.99.99.99"

            self.schema.User.insert([usertutu1, usertutu2])

            for record in self.schema.User:
                print(record)

            self.schema.commit()

    def test_04_update(self):
        """Update some records"""
        with self.schema:
            oldrecords = []
            newrecords = []
            for record in self.schema.User.select(lambda user: user.Name.in_('Aymeric', 'Marie')):
                oldrecords.append(record)
                newrecord = record.clone()
                newrecord.Name = newrecord.Name + '*'
                newrecords.append(newrecord)

            self.schema.User.update(oldrecords, newrecords)

            for record in self.schema.User:
                print(record)

            self.schema.commit()

    def test_05_delete(self):
        """Delete some records"""
        with self.schema:
            usertiti = self.schema.User.new()
            usertiti.Name = "Titi"
            usertiti.Age = 99
            usertiti.PhoneNumber = "99.99.99.99.99"
            self.schema.User.delete(usertiti)

            for record in self.schema.User:
                print(record)

            usertutu1 = self.schema.User.new()
            usertutu1.Name = "Tutu-1"
            usertutu1.Age = 15
            usertutu1.PhoneNumber = "08.08.99.99.99"

            usertutu2 = self.schema.User.new()
            usertutu2.Name = "Tutu-2"
            usertutu2.Age = 51
            usertutu2.PhoneNumber = "06.06.99.99.99"

            self.schema.User.delete([usertutu1, usertutu2])

            for record in self.schema.User:
                print(record)

            self.schema.commit()

if __name__ == "__main__":
    load_dotenv()
    configuration = DSConfiguration('test/database.yml')
    log = DSLogger(configuration)
    log.open()
    unittest.main()
    log.close()
