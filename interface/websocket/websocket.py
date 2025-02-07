"""
Test program (FastAPI - WebSocket)
"""

# pylint: disable=eval-used
# pylint: disable=unused-argument

import json

from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect

from interface.authentication import decrypt_user_web
from interface.db import get_db, schema

app = FastAPI()

# ------------------
# WebSocket method
# ------------------

async def websocket_service_message(websocket, user, message):
    """Send a message to all connections"""
    for connection in active_connections:
        data = {
            "action": "message",
            "parameters" : {
                "message": f"{user['sub']}: {message}"
            }
        }
        await connection.send_text(json.dumps(data))

async def websocket_service_schema(websocket, user):
    """Send the current schema"""
    data = {
        "action": "schema",
        "parameters" : {
            "schema": schema.to_dict()
        }
    }
    await websocket.send_text(json.dumps(data))

async def websocket_service_table(websocket, user, table):
    """Send records from a table"""
    with get_db():
        records = [record.to_dict() for record in schema[table]]

    data = {
        "action": "table",
        "parameters" : {
            "table": table,
            "records" : records
        }
    }
    await websocket.send_text(json.dumps(data))

# ------------------
# WebSocket handling
# ------------------

active_connections = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, user: dict = Depends(decrypt_user_web)):
    """Gestion des connexions WebSocket sécurisées."""
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            data = json.loads(await websocket.receive_text())
            await eval("websocket_service_" + data['action'])(websocket, user, **data['parameters'])
    except WebSocketDisconnect:
        active_connections.remove(websocket)
