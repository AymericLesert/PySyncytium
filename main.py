"""
Main program
"""

import json
import traceback
from schema.schema import DSSchema

schema = {
        'Name': 'Syncytium',
        'Description' : 'Schéma de test',
        'Tables' : {
                'User': {
                    'Description' : 'Liste des utilisateurs',
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
    db = DSSchema(schema)
    print(json.dumps(db.to_dict(), sort_keys=False, indent=2))
    print(db.User.where(lambda t: t.Name.operator_in('Aymeric', 'Marie')))
    print(db.User.where(lambda t: (t.Name == 'Aymeric') & (t.Age > 24) & t.PhoneNumber
                                                                        .operator_in('01', '02'))
                                                       .operator_not())
    print(db.User.where(lambda t: (t.Name == 'Aymeric').operator_and(t.Age > 24,
                                                                     t.PhoneNumber
                                                                        .operator_in('01', '02'))
                                                       .operator_not()))
except:  # pylint: disable=bare-except
    traceback.print_exc()
_ = input()
