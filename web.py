# -*- coding: utf-8 -*-

"""
Test program (FastAPI - FrontEnd)
"""

from interface.web.web import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080, log_config=None)
