"""
Main program
"""

import json
import traceback

from schema.schema import DSSchema
from database.databasemysql import DSDatabaseMySQL

schema = {
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

try:
    schema = DSSchema(schema)
    print(json.dumps(schema.to_dict(), sort_keys=False, indent=2))

    with DSDatabaseMySQL("localhost", "root", "6t-8ItCG$%oIh47E=") as db:
        print("connected", db.is_connected)
        schema.database = db

        print(json.dumps(db.get_description("Syncytium"), sort_keys=False, indent=2))

        userToto = schema.User.new()
        userToto.Name = "Toto"
        userToto.Age = 99
        userToto.PhoneNumber = "99.99.99.99.99"

        userTata = schema.User.new()
        userTata.Name = "Tata"
        userTata.Age = 88
        userTata.PhoneNumber = "88.99.99.99.99"

        db.begin_transaction()
        schema.User.delete([userToto, userTata])
        db.commit()

        db.begin_transaction()
        schema.User.insert([userToto, userTata])
        db.commit()

        db.begin_transaction()
        userTutu = userToto.clone()
        userTutu.PhoneNumber = "77.77"
        userTutu.Age = 1
        schema.User.update(userToto, userTutu)
        db.commit()

        for record in schema.User:
            newrecord = record.clone()
            newrecord.Name = record.Name + "*"
            print('current', record)
            print('new', newrecord)

        for record in schema.User.select(lambda user: user.Name.in_('Aymeric', 'Marie')):
            print(record)
            print(record.Name)
except:  # pylint: disable=bare-except
    traceback.print_exc()
_ = input()
