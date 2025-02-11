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

    log.close()
