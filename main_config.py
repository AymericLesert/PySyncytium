# -*- coding: utf-8 -*-

"""
Test program (Configuration)
"""

import json
from dotenv import load_dotenv

from configuration.configuration import DSConfiguration

load_dotenv()

configuration = DSConfiguration('config.yml')

print(json.dumps(configuration.to_dict(), sort_keys=False, indent=2))
print('format', configuration.items.logging.formatters.standard.format)
print('hostname', configuration.items.database.hostname)
print('username', configuration.items.database.username)
print('essai', configuration.items.database.essai)
print('APPLICATION', configuration.application)
print('VERSION', configuration.version)
print('to_dict', configuration.items.to_dict())
