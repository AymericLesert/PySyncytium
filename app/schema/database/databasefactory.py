# -*- coding: utf-8 -*-

"""Create a database from a dictionary"""

from exception.exceptiondatabaseunknown import DSExceptionDatabaseUnknown
from .databasemysql import DSDatabaseMySQL

def factory(configuration):
    """Create a database instance"""
    databases = { "MySQL" : DSDatabaseMySQL }
    
    klass = configuration.get('class', 'MySQL')
    if klass not in databases:
        raise DSExceptionDatabaseUnknown(f"Database '{klass}' not known")

    parameters = configuration.get('parameters', {})
    if isinstance(parameters, dict):
        database_parameters = parameters
    else:
        database_parameters = {}
        for field in parameters.items.keys():
            database_parameters[field] = parameters[field]

    return databases[klass](**database_parameters)
