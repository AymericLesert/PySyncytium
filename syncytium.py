# -*- coding: utf-8 -*-
# pylint: disable=ungrouped-imports

"""
Main program (Syncytium)
- api
- web
- websocket
"""

import argparse
import hashlib
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

from interface.schemas import DSSchemas

load_dotenv()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start one of the piece of Syncytium application")
    parser.add_argument('--name', type=str, required=True, help="api, web or websocket (or migrate)")
    parser.add_argument('--client', type=int, required=False, help='Client')
    parser.add_argument('--username', type=str, required=False, help='Username')
    parser.add_argument('--password', type=str, required=False, help='Password')
    args = parser.parse_args()

    DSSchemas().load('config.yml')
    DSSchemas().open()

    if args.name == "api":
        from interface.api.api import app
        import uvicorn
        uvicorn.run(app,
                    host=DSSchemas().configuration.items.interface.api.server.hostname,
                    port=DSSchemas().configuration.items.interface.api.server.port,
                    log_config=None)
    elif args.name == "web":
        from interface.web.web import app
        import uvicorn
        uvicorn.run(app,
                    host=DSSchemas().configuration.items.interface.web.server.hostname,
                    port=DSSchemas().configuration.items.interface.web.server.port,
                    log_config=None)
    elif args.name == "websocket":
        from interface.websocket.websocket import app
        import uvicorn
        uvicorn.run(app,
                    host=DSSchemas().configuration.items.interface.websocket.server.hostname,
                    port=DSSchemas().configuration.items.interface.websocket.server.port,
                    log_config=None)
    elif args.name == "migrate":
        with DSSchemas().get_session() as schema:
            with schema:
                schema.migrate()
    elif args.name == "user":
        with DSSchemas().get_session() as schema:
            with schema:
                schema.User.delete(list(schema.User.select(lambda record: record.Login == args.username)))

                h = hashlib.new(DSSchemas().configuration.items.interface.api.password.algorithm)
                h.update(args.password.encode('utf-8'))

                user_api = schema.User.new()
                user_api.Interface = DSSchemas.Interface.API.value
                user_api.Login = args.username
                user_api.Password = h.hexdigest()
                user_api.ClientId = args.client

                h = hashlib.new(DSSchemas().configuration.items.interface.web.password.algorithm)
                h.update(args.password.encode('utf-8'))

                user_web = schema.User.new()
                user_web.Interface = DSSchemas.Interface.WEB.value
                user_web.Login = args.username
                user_web.Password = h.hexdigest()
                user_web.ClientId = args.client

                schema.User.insert([user_api, user_web])
                schema.commit()
    elif args.name == "key.new":
        print("Key generated to encrypt and decrypt database password :")
        print("PSPASSWORD_KEY=", Fernet.generate_key().decode('utf-8'))
    elif args.name == "key.encrypt":
        cipher_suite = Fernet(bytes(os.getenv("PSPASSWORD_KEY"), 'utf-8'))
        print("Password encrypted :", cipher_suite.encrypt(bytes(args.password, 'utf-8')).decode('utf-8'))
    elif args.name == "key.decrypt":
        cipher_suite = Fernet(bytes(os.getenv("PSPASSWORD_KEY"), 'utf-8'))
        print("Password encrypted :", cipher_suite.decrypt(bytes(args.password, 'utf-8')).decode('utf-8'))

    DSSchemas().close()
