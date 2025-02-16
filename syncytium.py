# -*- coding: utf-8 -*-
# pylint: disable=ungrouped-imports

"""
Main program (Syncytium)
- api
- web
- websocket
"""

import argparse
from dotenv import load_dotenv

from configuration.configuration import DSConfiguration
from logger.logger import DSLogger
from app.schema.database.databasefactory import factory as databasefactory
from app.schema.schema import DSSchema

load_dotenv()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start one of the piece of Syncytium application")
    parser.add_argument('--name', type=str, required=True, help="api, web or websocket")
    args = parser.parse_args()

    configuration = DSConfiguration('config.yml')
    log = DSLogger(configuration)
    log.open()

    if args.name == "api":
        from interface.api.api import app
        import uvicorn
        uvicorn.run(app,
                    host=configuration.items.interface.api.hostname,
                    port=configuration.items.interface.api.port,
                    log_config=None)
    elif args.name == "web":
        from interface.web.web import app
        import uvicorn
        uvicorn.run(app,
                    host=configuration.items.interface.web.hostname,
                    port=configuration.items.interface.web.port,
                    log_config=None)
    elif args.name == "websocket":
        from interface.websocket.websocket import app
        import uvicorn
        uvicorn.run(app,
                    host=configuration.items.interface.websocket.hostname,
                    port=configuration.items.interface.websocket.port,
                    log_config=None)
    elif args.name == "root":
        schema = DSSchema(databasefactory(configuration.items.main.database), configuration.items.main.schema)
        with schema:
            schema.migrate()

    log.close()
