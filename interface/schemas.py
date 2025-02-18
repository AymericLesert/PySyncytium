# -*- coding: utf-8 -*-
#pylint: disable=too-few-public-methods

"""
This module stores the schemas and the database session
"""

from enum import Enum

from configuration.configuration import DSConfiguration
from logger.logger import DSLogger
from logger.loggerobject import DSLoggerObject

from app.schema.database.databasefactory import factory as databasefactory
from app.schema.schema import DSSchema

class DSSchemas:
    """
    This class stores all schemas and sessions
    """

    class Interface(Enum):
        """Enumeration of the kind of interface"""
        WEB = 0
        API = 1

    class Session:
        """This class attaches a session to all schemas"""
        def __enter__(self):
            return self.__session

        def __exit__(self, *args):
            DSSchemas().release_session(self.__name, self.__session)

        def __init__(self, name, session):
            self.__name = name
            self.__session = session

    class Sessions(DSLoggerObject):
        """Store the list of sessions by name"""

        @property
        def configuration(self):
            """Retrieves the global configuration"""
            if self.__configuration is None:
                return DSConfiguration()
            return self.__configuration

        def load(self, filename):
            """Load the global configuration"""
            self.__configuration = DSConfiguration(filename)
            self.__log = DSLogger(self.__configuration)
            self.info(f"Configuration '{filename}' loaded")

        def open(self):
            """Open schemas"""
            if self.__log is not None:
                self.__log.open()
            self.info("Schemas opened")

        def get_session(self, client = None, application = None):
            """Return a schema instance ready to get access to the database"""
            name = ""
            if not client is None:
                name = client
            if name != "" :
                name += "."
            if not application is None:
                name += application

            self.debug(f"Getting a session '{name}' ...")

            if not name in self.__schemas:
                self.__schemas[name] = []

            if not name in self.__schemas_availables:
                self.__schemas_availables[name] = []

            if len(self.__schemas_availables[name]) > 0:
                self.info(f"Session '{name}' recycled")
                return DSSchemas.Session(name, self.__schemas_availables.pop())

            newschema = None
            if name == "":
                newschema = DSSchema(databasefactory(self.configuration.items.main.database), self.configuration.items.main.schema)

            if newschema is None:
                self.info(f"Session '{name}' unknown")
                return None

            self.info(f"Session '{name}' created")

            self.__schemas[name].append(newschema)
            return DSSchemas.Session(name, newschema)

        def release_session(self, name, session):
            """Release a session and set it as free for a new session"""
            if name in self.__schemas and session is not None:
                self.info(f"Session '{name}' released")
                self.__schemas_availables[name].append(session)

        def close(self):
            """Close schemas"""
            if self.__log is not None:
                self.__log.close()
            self.info("Schemas closed")

        def __init__(self):
            super().__init__()
            self.__configuration = None
            self.__log = None
            self.__schemas = {}
            self.__schemas_availables = {}

    __instance = None

    def __new__(cls):
        if DSSchemas.__instance is None:
            DSSchemas.__instance = object.__new__(cls)
            DSSchemas.__instance._sessions = DSSchemas.Sessions()
        return DSSchemas.__instance._sessions
