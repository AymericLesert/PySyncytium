# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module handles the database connexion for MySQL instance.
"""

import json

import mysql.connector

from exception.exceptiondatabasenotconnected import DSExceptionDatabaseNotConnected
from exception.exceptiondatabaserequest import DSExceptionDatabaseRequest

from .database import DSDatabase
from .cursor import DSCursor

class DSDatabaseMySQL(DSDatabase):
    """This class implements a connexion to a MySQL Database"""

    def connect(self):
        """This method describes the connection to MySQL"""
        self.debug(f"Connecting to the database '{self.__host}' with user '{self.__username}' ...")
        try:
            self.__database = mysql.connector.connect(host=self.__host, user=self.__username, password=self.__password)
            self.__database.start_transaction()
            self.__transaction = self.__database.cursor()
            self.info(f"Database '{self.__host}' with user '{self.__username}' connected")
        except Exception:
            self.exception(f"Error on connection to the database '{self.__host}' with user '{self.__username}'")
            self.disconnect()
        return self

    @property
    def isconnected(self):
        """Return if the connection is done"""
        try:
            return self.__database is not None and self.__database.is_connected()
        except:
            return False

    @property
    def schema(self):
        """Retrieve a JSON description of the tables from a given schema"""
        self.debug(f"Retrieveing the schema '{self.__schema}' ...")

        if not self.isconnected:
            raise DSExceptionDatabaseNotConnected(f"No connection to the database '{self.__host}' with user '{self.__username}'")

        structure = { 'Name': self.__schema, 'Tables' : {} }

        if self.isverbose:
            self.verbose(f"USE `{self.__schema}`")
        self.__transaction.execute(f"USE `{self.__schema}`")
        
        if self.isverbose:
            self.verbose("SHOW TABLES")
        self.__transaction.execute("SHOW TABLES")

        for (tablename,) in self.__transaction.fetchall():
            structuretable = { 'Name': tablename, 'Fields': {} }

            if self.isverbose:
                self.verbose(f"DESCRIBE `{tablename}`")
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
        
        self.info(f"The schema '{self.__schema}' is retrieved")
        
        if self.isverbose:
            self.verbose(json.dumps(structure, sort_keys=True, indent=2))

        return structure

    def insert(self, tablename, fields, values):
        """Return the list of values inserted into a table"""
        query = "INSERT INTO `" + self.__schema + "`.`" + tablename + "`" + \
                "(" + ", ".join(["`" + name + "`" for name in fields]) + ") " + \
                "VALUES(" + ", ".join(["%s" for _ in fields]) + ")"

        self.debug(f"Executing '{query}' ...")

        if not self.isconnected:
            raise DSExceptionDatabaseNotConnected(f"No connection to the database '{self.__host}' with user '{self.__username}'")

        items = []
        if isinstance(values, (list, tuple)):
            for value in values:
                items.append(tuple(value[name] for name in fields))
        else:
            items.append(tuple(values[name] for name in fields))

        count = len(items)
        self.verbose(f"Inserting {count} lines ...")
        try:
            if count == 1:
                self.__transaction.execute(query, items[0])
                self.info(f"1 row inserted into '{tablename}'")
            elif count > 1:
                self.__transaction.executemany(query, items)
                self.info(f"{count} rows inserted into '{tablename}'")
            else:
                self.info(f"No data inserted into '{tablename}'")
        except:
            raise DSExceptionDatabaseRequest(f"Error on executing the request '{query}'")

        return values

    def select(self, tablename, fields, clause = None):
        """Return a cursor to the selection of the dstable"""

        query = "SELECT " + ", ".join(["`" + name + "`" for name in fields]) + " " + \
                "FROM `" + self.__schema + "`.`" + tablename + "`"
        if clause is not None:
            query += " WHERE " + clause

        self.debug(f"Executing '{query}' ...")

        if not self.isconnected:
            raise DSExceptionDatabaseNotConnected(f"No connection to the database '{self.__host}' with user '{self.__username}'")

        try:
            cursor = self.__database.cursor()
            cursor.execute(query)

            self.info(f"Selecting data from '{tablename}' where '{query}') ...")
            return DSCursor(cursor, tablename, fields).set_user(self.user)
        except:
            raise DSExceptionDatabaseRequest(f"Error on executing the request '{query}'")

    def update(self, tablename, fields, oldvalue, newvalue):
        """Return the new value"""

        query = "UPDATE `" + self.__schema + "`.`" + tablename + "` " + \
                "SET " + ", ".join(["`" + field + "` = %s " for field in fields]) + \
                "WHERE " + "and ".join(["`" + field + "` = %s " for field in fields]) 

        self.debug(f"Executing '{query}' ...")

        if not self.isconnected:
            raise DSExceptionDatabaseNotConnected(f"No connection to the database '{self.__host}' with user '{self.__username}'")

        if oldvalue == newvalue:
            return newvalue

        values = []
        for field in fields:
            values.append(newvalue[field])
        for field in fields:
            values.append(oldvalue[field])

        try:
            self.__transaction.execute(query, tuple(values))
            self.info(f"{self.__transaction.mysql_affected_rows()} rows updated into '{tablename}'")
        except:
            raise DSExceptionDatabaseRequest(f"Error on executing the request '{query}'")

        return newvalue

    def delete(self, tablename, fields, values):
        """Return the list of values removed"""

        query = "DELETE FROM `" + self.__schema + "`.`" + tablename + "` " + \
                "WHERE " + "and ".join(["`" + field + "` = %s " for field in fields]) 

        self.debug(f"Executing '{query}' ...")

        if not self.isconnected:
            raise DSExceptionDatabaseNotConnected(f"No connection to the database '{self.__host}' with user '{self.__username}'")

        items = []
        if isinstance(values, (list, tuple)):
            for value in values:
                items.append(tuple(value[name] for name in fields))
        else:
            items.append(tuple(values[name] for name in fields))

        count = len(items)
        self.verbose(f"Removing {count} lines ...")
        try:
            if count == 1:
                self.__transaction.execute(query, items[0])
                self.info(f"{self.__transaction.mysql_affected_rows()} row removed into '{tablename}'")
            elif count > 1:
                self.__transaction.executemany(query, items)
                self.info(f"{self.__transaction.mysql_affected_rows()} rows removed into '{tablename}'")
            else:
                self.info(f"No data removed into '{tablename}'")
        except:
            raise DSExceptionDatabaseRequest(f"Error on executing the request '{query}'")

        return values

    def commit(self):
        """Commit the current transaction"""
        self.debug("Committing ...")

        if not self.isconnected:
            raise DSExceptionDatabaseNotConnected(f"No connection to the database '{self.__host}' with user '{self.__username}'")

        try:
            self.__database.rollback()
            self.info("Commit done")
            self.__database.start_transaction()
        except:
            self.exception("Error on committing")

    def rollback(self):
        """Rollback the current transaction"""
        self.debug("Rollbacking ...")

        if not self.isconnected:
            raise DSExceptionDatabaseNotConnected(f"No connection to the database '{self.__host}' with user '{self.__username}'")

        try:
            self.__database.rollback()
            self.info("Rollback done")
            self.__database.start_transaction()
        except:
            self.exception("Error on rollbacking")

    def disconnect(self):
        """This method describes the disconnection to MySQL"""
        self.debug(f"Disconnecting to the database '{self.__host}' with user '{self.__username}' ...")

        if self.__transaction is not None:
            try:
                self.__transaction.close()
            except:
                self.exception("Error on closing the transaction")
            self.__transaction = None

        if self.__database is not None:
            try:
                self.__database.close()
            except:
                self.exception("Error on disconnecting the database")
            self.__database = None

        self.info(f"Database '{self.__host}' with user '{self.__username}' disconnected")
        return self

    def __init__(self, host, username, password, schema):
        super().__init__()
        self.__host = host
        self.__username = username
        self.__password = password
        self.__schema = schema
        self.__database = None
        self.__transaction = None
