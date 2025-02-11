# -*- coding: utf-8 -*-

"""
Test program (FastAPI - API)
"""

from interface.api.api import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_config=None)
