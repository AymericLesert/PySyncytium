# -*- coding: utf-8 -*-

"""
Test program (Logger)
"""

from dotenv import load_dotenv

from configuration.configuration import DSConfiguration
from logger.logger import DSLogger
from logger.loggerobject import DSLoggerObject

load_dotenv()

class Sample(DSLoggerObject):
    def test(self):
        self.info("essai")

configuration = DSConfiguration('config.yml')
log = DSLogger(configuration)
log.open()
log.verbose("aymeric", "DSLog", __name__, "Test verbose")
try:
    raise Exception('toto')
except Exception:
    log.exception("aymeric", "DSLog", __name__, "Test exception")
Sample().test()
log.close()
