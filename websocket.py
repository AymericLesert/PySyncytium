# -*- coding: utf-8 -*-

"""
Test program (FastAPI - WebSocket)
"""

from interface.websocket.websocket import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8081, log_config=None)
