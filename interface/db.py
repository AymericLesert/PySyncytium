# -*- coding: utf-8 -*-

"""
Test program (FastAPI - FrontEnd)
"""

# pylint: disable=eval-used
# pylint: disable=unused-argument

import json
import traceback
import os
from dotenv import load_dotenv

from schema.schema import DSSchema
from database.databasemysql import DSDatabaseMySQL

load_dotenv()

SCHEMA = {
        'Name': 'Syncytium',
        'Description' : 'Schéma de test',
        'Tables' : {
                'User': {
                    'Description' : 'Liste des utilisateurs',
                    'Key' : 'Name',
                    'Fields' : {
                        'Name': {
                            'Description': 'Nom et prénom de l\'utilisateur', 
                            'Type' : 'String',
                            'MaxLength': 80
                        },
                        'PhoneNumber' : {
                            'Type' : 'String',
                            'MaxLength': 14
                        },
                        'Age' : {
                            'Type' : 'Integer'
                        }
                    }
                }
        }
    }

def get_db():
    """Retrieve a database instance"""
    db = DSDatabaseMySQL(os.getenv("DATABASE_HOSTNAME", "localhost"),
                         os.getenv("DATABASE_USERNAME"),
                         os.getenv("DATABASE_PASSWORD"))
    db.connect()
    schema.database = db
    return db

try:
    schema = DSSchema(SCHEMA)
    print(json.dumps(schema.to_dict(), sort_keys=False, indent=2))
except:  # pylint: disable=bare-except
    traceback.print_exc()
