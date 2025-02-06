"""
This module handles the database connexion for MySQL instance.
"""

import mysql.connector

from .database import DSDatabase
from .cursor import DSCursor

class DSDatabaseMySQL(DSDatabase):
    """This class implements a connexion to a MySQL Database"""

    def connect(self):
        """This method describes the connection to MySQL"""
        self.__database = mysql.connector.connect(host=self.__host, user=self.__username, password=self.__password)
        return self

    @property
    def is_connected(self):
        """Return if the connection is done"""
        return self.__database is not None and self.__database.is_connected()

    def get_description(self, schema):
        """Retrieve a JSON description of the tables from a given schema"""
        structure = { 'Name': schema, 'Tables' : {} }
        self.begin_transaction()
        self.__transaction = self.__database.cursor()
        self.__transaction.execute(f"USE `{schema}`")
        self.__transaction.execute("SHOW TABLES")
        for (tablename,) in self.__transaction.fetchall():
            structuretable = { 'Name': tablename, 'Fields': {} }
            self.__transaction.execute(f"DESCRIBE `{tablename}`")
            for fieldname, fieldtype, nullable, primarykey, defaultvalue, _ in self.__transaction.fetchall():
                structurefield = {
                    'Name': fieldname, 
                    'Type': fieldtype,
                    'DefaultValue': defaultvalue,
                    'Nullable' : nullable
                    }
                if primarykey == 'PRI':
                    structuretable['Key'] = fieldname
                structuretable['Fields'][fieldname] = structurefield
            structure['Tables'][tablename] = structuretable
        self.__database.rollback()
        return structure

    def begin_transaction(self):
        """Start a new transaction"""
        print("begin_transaction")
        if self.__transaction is not None:
            return
        self.__database.start_transaction()
        self.__transaction = self.__database.cursor()

    def insert(self, dstable, values):
        """Return the list of keys created while inserting the list of values"""
        query = "INSERT INTO `" + dstable.schema.name + "`.`" + dstable.name + "`" + \
                "(" + ", ".join(["`" + name + "`" for name in dstable.fields]) + ") " + \
                "VALUES(" + ", ".join(["%s" for _ in dstable.fields]) + ")"
        keys = []
        items = []
        if isinstance(values, list):
            for value in values:
                items.append(tuple(value[name] for name in dstable.fields))
                keys.append(value[dstable.key])
        else:
            items.append(tuple(values[name] for name in dstable.fields))
            keys.append(values[dstable.key])
        count = len(items)
        print(query, items)
        if count == 1:
            self.__transaction.execute(query, items[0])
        elif count > 1:
            self.__transaction.executemany(query, items)
        return keys

    def select(self, dstable, clause = None):
        """Return a cursor to the selection of the dstable"""
        cursor = self.__database.cursor()
        query = "SELECT " + ", ".join(["`" + name + "`" for name in dstable.fields]) + " " + \
                "FROM `" + dstable.schema.name + "`.`" + dstable.name + "`"
        if clause is not None:
            query += " WHERE " + clause.tomysql()
        print(query)
        cursor.execute(query)
        return DSCursor(cursor, dstable)

    def update(self, dstable, oldvalue, newvalue):
        """Return the key updated"""
        if oldvalue[dstable.key] != newvalue[dstable.key]:
            return None
        if oldvalue == newvalue:
            return [newvalue[dstable.key]]
        fields = []
        values = []
        for field in dstable.fields:
            if oldvalue[field] != newvalue[field]:
                fields.append(field)
                values.append(newvalue[field])
        values.append(newvalue[dstable.key])
        query = "UPDATE `" + dstable.schema.name + "`.`" + dstable.name + "` " + \
                "SET " + ", ".join(["`" + field + "` = %s " for field in fields]) + \
                "WHERE `" + dstable.key + "` = %s" 
        print(query, values)
        self.__transaction.execute(query, tuple(values))
        return [newvalue[dstable.key]]

    def delete(self, dstable, values):
        """Return the list of keys removed"""
        keys = []
        if isinstance(values, list):
            for value in values:
                keys.append(tuple([value[dstable.key]]))
        else:
            print(values)
            keys.append(tuple([values[dstable.key]]))

        count = len(keys)
        query = "DELETE FROM `" + dstable.schema.name + "`.`" + dstable.name + "` " + \
                "WHERE `" + dstable.key + "` = %s" 
        print(query, keys)
        if count == 1:
            self.__transaction.execute(query, keys[0])
        elif count > 1:
            self.__transaction.executemany(query, keys)
        return keys

    def end_transaction(self):
        """Close the current transaction"""
        print("end_transaction")
        if self.__transaction is not None:
            self.__transaction.close()
        self.__transaction = None

    def commit(self):
        """Commit the current transaction"""
        self.__database.commit()
        self.end_transaction()

    def rollback(self):
        """Rollback the current transaction"""
        self.__database.rollback()
        self.end_transaction()

    def disconnect(self):
        """This method describes the disconnection to MySQL"""
        self.__database.close()
        self.__database = None
        return self

    def __init__(self, host, username, password):
        self.__host = host
        self.__username = username
        self.__password = password
        self.__database = None
        self.__transaction = None
