# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module handles the database connexion for MySQL instance.
"""

import os
import json
import jinja2
from cryptography.fernet import Fernet

import mysql.connector

from exception.exceptiondatabasenotconnected import DSExceptionDatabaseNotConnected
from exception.exceptiondatabaserequest import DSExceptionDatabaseRequest
from exception.exceptiondatabaseunknown import DSExceptionDatabaseUnknown

from .database import DSDatabase
from .databasecursor import DSDatabaseCursor

class DSDatabaseMySQL(DSDatabase):
    """This class implements a connexion to a MySQL Database"""

    SCRIPT_CREATE_SCHEMA = """
        CREATE SCHEMA `{{Name}}`;
        USE `{{Name}}`;
        {% for tablename in Tables %}
        {% set table = Tables[tablename] %}
        CREATE TABLE `{{table.Name}}`
            (
            {% for fieldname in table.Fields %}
                {% set field = table.Fields[fieldname] %}
                {% set type = "" %}
                {% set default = "" %}
                {% if field.Type == "String" %}
                    {% set type = "VARCHAR(" ~ field.MaxLength ~ ")" %}
                    {% if field.DefaultValue is not none %}
                    {% set default = " DEFAULT '" ~ field.DefaultValue ~ "'" %}
                    {% endif %}
                {% elif field.Type == "Integer" %}
                    {% set type = "INT" %}
                    {% if field.DefaultValue is not none %}
                    {% set default = " DEFAULT " ~ field.DefaultValue %}
                    {% endif %}
                {% else %}
                    {% set type = "VARCHAR(2048)" %}
                {% endif %}
                {% set notnull = "" %}
                `{{field.Name}}` {{type}}{{notnull}}{{default}},
            {% endfor %}
            {% set ns = namespace(primarykey="") %}
            {% for index in range(table.Key | length) %}
                {% if ns.primarykey == "" %}
                    {% set ns.primarykey = "`" ~ table.Key[index] ~ "`" %}
                {% else %}
                    {% set ns.primarykey = ns.primarykey ~ ", `" ~ table.Key[index] ~ "`" %}
                {% endif %}
            {% endfor %}
                CONSTRAINT PK_{{table.Name}} PRIMARY KEY ({{ns.primarykey}})
            );
        {% endfor %}
    """

    SCRIPT_CREATE_USER = """
        CREATE USER IF NOT EXISTS '{{username}}'@'{{hostname}}';
        ALTER USER '{{username}}'@'{{hostname}}' IDENTIFIED WITH 'mysql_native_password' AS '{{password}}';
        GRANT {{privileges}} ON `{{schema}}`.* TO '{{username}}'@'{{hostname}}' WITH GRANT OPTION;
        FLUSH PRIVILEGES;
    """

    def to_dict(self):
        """Retrieves the database instance into a dictionary"""
        return {
            'hostname': self.__hostname,
            'username': self.__username,
            'password': self.__password,
            'schema': self.__schema
            }

    def connect(self):
        """This method describes the connection to MySQL"""
        self.debug(f"Connecting to the database '{self.__hostname}' with user '{self.__username}' ...")
        try:
            cipher_suite = Fernet(bytes(os.getenv("PSPASSWORD_KEY"), 'utf-8'))
            password = cipher_suite.decrypt(bytes(self.__password, 'utf-8')).decode('utf-8')
            self.__database = mysql.connector.connect(host=self.__hostname, user=self.__username, password=password)
            self.__database.start_transaction()
            self.__transaction = self.__database.cursor()
            self.info(f"Database '{self.__hostname}' with user '{self.__username}' connected")
        except:
            self.exception(f"Error on connection to the database '{self.__hostname}' with user '{self.__username}'")
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
            raise DSExceptionDatabaseNotConnected(f"No connection to the database '{self.__hostname}' with user '{self.__username}'")

        structure = { 'Name': self.__schema, 'Tables' : {} }

        if self.isverbose:
            self.verbose(f"USE `{self.__schema}`")
        try:
            self.__transaction.execute(f"USE `{self.__schema}`")
        except Exception as exc:
            raise DSExceptionDatabaseUnknown(f"Schema '{self.__schema}' unknown") from exc
        if self.isverbose:
            self.verbose("SHOW TABLES")
        self.__transaction.execute("SHOW TABLES")

        for (tablename,) in self.__transaction.fetchall():
            structuretable = { 'Name': tablename, 'Fields': {}, 'Key': [] }

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
                    structuretable['Key'].append(fieldname)
                structuretable['Fields'][fieldname] = structurefield
            structure['Tables'][tablename] = structuretable
        self.info(f"The schema '{self.__schema}' is retrieved")

        if self.isverbose:
            self.verbose(json.dumps(structure, sort_keys=True, indent=2))

        return structure

    def __execute_script(self, template_sql, items):
        """Execute a SQL Script"""
        template = jinja2.Environment(loader=jinja2.BaseLoader()).from_string(template_sql)
        script = template.render(**items)
        self.verbose(script)
        for request in script.split(";"):
            if request.strip() == '':
                continue
            self.info("Executing :")
            self.info(request)
            self.__transaction.execute(request)
            self.info("Done")

    def migrate(self, schema, database, allprivileges):
        """Create or upgrade a schema from the json description"""
        if self.isverbose:
            self.verbose("Migrating the schema :")
            self.verbose(json.dumps(schema, indent=2))

        if schema is None or schema.get('Name', None) is None:
            raise DSExceptionDatabaseUnknown("Schema non correctly defined")

        if not allprivileges:
            database['privileges'] = "DELETE, INSERT, UPDATE, SELECT"

        if not self.isconnected:
            raise DSExceptionDatabaseNotConnected(f"No connection to the database '{self.__hostname}' with user '{self.__username}'")

        try:
            self.__transaction.execute(f"USE `{schema.get('Name')}`")
            self.info(f"Schema to upgrade : {schema.get('Name')}")
            # TODO : Upgrade the schema
            return False
        except:
            self.info(f"Creating the schema '{schema.get('Name')}' ...")

            try:
                self.__execute_script(DSDatabaseMySQL.SCRIPT_CREATE_SCHEMA, schema)
            except:
                self.exception("Error on migrating the schema ...")
                raise

            if not allprivileges:
                self.info(f"Granting the schema '{schema.get('Name')}' ...")

                try:
                    self.__execute_script(DSDatabaseMySQL.SCRIPT_CREATE_USER, database)
                except:
                    self.exception("Error on granting the schema ...")
                    raise

            return True

    def insert(self, tablename, fields, values):
        """Return the list of values inserted into a table"""
        query = "INSERT INTO `" + self.__schema + "`.`" + tablename + "`" + \
                "(" + ", ".join(["`" + name + "`" for name in fields]) + ") " + \
                "VALUES(" + ", ".join(["%s" for _ in fields]) + ")"

        self.debug(f"Executing '{query}' ...")

        if not self.isconnected:
            raise DSExceptionDatabaseNotConnected(f"No connection to the database '{self.__hostname}' with user '{self.__username}'")

        items = []
        try:
            if isinstance(values, (list, tuple)):
                for value in values:
                    items.append(tuple(value[name] for name in fields))
            else:
                items.append(tuple(values[name] for name in fields))
        except Exception as exc:
            self.exception(f"Error on extracting data from '{query}'")
            raise DSExceptionDatabaseRequest(f"Error on extracting data from '{query}'") from exc

        count = len(items)
        self.verbose(f"Inserting {count} lines ...")
        if self.isverbose:
            for item in items:
                self.verbose(str(item))
        try:
            if count == 1:
                self.__transaction.execute(query, items[0])
                self.info(f"{self.__transaction.rowcount} row inserted into '{tablename}'")
            elif count > 1:
                self.__transaction.executemany(query, items)
                self.info(f"{self.__transaction.rowcount} rows inserted into '{tablename}'")
            else:
                self.info(f"No data inserted into '{tablename}'")
        except Exception as exc:
            self.exception(f"Error on executing the request '{query}'")
            raise DSExceptionDatabaseRequest(f"Error on executing the request '{query}'") from exc

        return values

    def select(self, tablename, fields, clause = None):
        """Return a cursor to the selection of the dstable"""

        query = "SELECT " + ", ".join(["`" + name + "`" for name in fields]) + " " + \
                "FROM `" + self.__schema + "`.`" + tablename + "`"
        if clause is not None:
            if isinstance(clause, str):
                query += " WHERE " + clause
            else:
                query += " WHERE " + clause.tomysql()

        self.debug(f"Executing '{query}' ...")

        if not self.isconnected:
            raise DSExceptionDatabaseNotConnected(f"No connection to the database '{self.__hostname}' with user '{self.__username}'")

        try:
            cursor = self.__database.cursor()
            cursor.execute(query)

            self.info(f"Selecting data from '{tablename}' where '{query}') ...")
            return DSDatabaseCursor(cursor, tablename, fields).set_user(self.user)
        except Exception as exc:
            self.exception(f"Error on executing the request '{query}'")
            raise DSExceptionDatabaseRequest(f"Error on executing the request '{query}'") from exc

    def update(self, tablename, fields, oldvalues, newvalues):
        """Return the new value"""

        query = "UPDATE `" + self.__schema + "`.`" + tablename + "` " + \
                "SET " + ", ".join(["`" + field + "` = %s " for field in fields]) + \
                "WHERE " + "and ".join(["`" + field + "` = %s " for field in fields]) 

        self.debug(f"Executing '{query}' ...")

        if not self.isconnected:
            raise DSExceptionDatabaseNotConnected(f"No connection to the database '{self.__hostname}' with user '{self.__username}'")

        items = []
        count = 0
        try:
            if isinstance(oldvalues, (list, tuple)):
                for oldvalue, newvalue in zip(oldvalues, newvalues):
                    if oldvalue == newvalue:
                        continue
                    subitems = []
                    for field in fields:
                        subitems.append(newvalue[field])
                    for field in fields:
                        subitems.append(oldvalue[field])
                    items.append(tuple(subitems))
                    count += 1
            elif oldvalues != newvalues:
                subitems = []
                for field in fields:
                    subitems.append(newvalues[field])
                for field in fields:
                    subitems.append(oldvalues[field])
                items.append(tuple(subitems))
                count += 1
        except Exception as exc:
            self.exception(f"Error on extracting data from '{query}'")
            raise DSExceptionDatabaseRequest(f"Error on extracting data from '{query}'") from exc

        self.verbose(f"Updating {count} lines ...")
        if self.isverbose:
            for item in items:
                self.verbose(str(item))
        try:
            if count == 1:
                self.__transaction.execute(query, items[0])
                self.info(f"{self.__transaction.rowcount} row updated into '{tablename}'")
            elif count > 1:
                self.__transaction.executemany(query, items)
                self.info(f"{self.__transaction.rowcount} rows updated into '{tablename}'")
            else:
                self.info(f"No data updated into '{tablename}'")
        except Exception as exc:
            self.exception(f"Error on executing the request '{query}'")
            raise DSExceptionDatabaseRequest(f"Error on executing the request '{query}'") from exc

        return newvalues

    def delete(self, tablename, fields, values):
        """Return the list of values removed"""

        query = "DELETE FROM `" + self.__schema + "`.`" + tablename + "` " + \
                "WHERE " + "and ".join(["`" + field + "` = %s " for field in fields]) 

        self.debug(f"Executing '{query}' ...")

        if not self.isconnected:
            raise DSExceptionDatabaseNotConnected(f"No connection to the database '{self.__hostname}' with user '{self.__username}'")

        items = []
        try:
            if isinstance(values, (list, tuple)):
                for value in values:
                    items.append(tuple(value[name] for name in fields))
            else:
                items.append(tuple(values[name] for name in fields))
        except Exception as exc:
            self.exception(f"Error on extracting data from '{query}'")
            raise DSExceptionDatabaseRequest(f"Error on extracting data from '{query}'") from exc

        count = len(items)
        self.verbose(f"Deleting {count} lines ...")
        if self.isverbose:
            for item in items:
                self.verbose(str(item))
        try:
            if count == 1:
                self.__transaction.execute(query, items[0])
                self.info(f"{self.__transaction.rowcount} row deleted into '{tablename}'")
            elif count > 1:
                self.__transaction.executemany(query, items)
                self.info(f"{self.__transaction.rowcount} rows deleted into '{tablename}'")
            else:
                self.info(f"No data deleted into '{tablename}'")
        except Exception as exc:
            self.exception(f"Error on executing the request '{query}'")
            raise DSExceptionDatabaseRequest(f"Error on executing the request '{query}'") from exc

        return values

    def commit(self):
        """Commit the current transaction"""
        self.debug("Committing ...")

        if not self.isconnected:
            raise DSExceptionDatabaseNotConnected(f"No connection to the database '{self.__hostname}' with user '{self.__username}'")

        try:
            self.__database.commit()
            self.info("Commit done")
            self.__database.start_transaction()
        except:
            self.exception("Error on committing")

    def rollback(self):
        """Rollback the current transaction"""
        self.debug("Rollbacking ...")

        if not self.isconnected:
            raise DSExceptionDatabaseNotConnected(f"No connection to the database '{self.__hostname}' with user '{self.__username}'")

        try:
            self.__database.rollback()
            self.info("Rollback done")
            self.__database.start_transaction()
        except:
            self.exception("Error on rollbacking")

    def disconnect(self):
        """This method describes the disconnection to MySQL"""
        self.debug(f"Disconnecting to the database '{self.__hostname}' with user '{self.__username}' ...")

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

        self.info(f"Database '{self.__hostname}' with user '{self.__username}' disconnected")
        return self

    def __init__(self, hostname, username, password, schema):
        super().__init__()
        self.__hostname = hostname
        self.__username = username
        self.__password = password
        self.__schema = schema
        self.__database = None
        self.__transaction = None
