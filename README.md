# PySyncytium

## D�marrage de l'API

```
cd PySyncytium
env\Script\activate
fastapi dev interface\api\api.py
```

## D�marrage du front HTML

```
cd PySyncytium
env\Script\activate
uvicorn interface.web.web:app --reload --port 8080
```

## D�marrage du serveur WebSocket

```
cd PySyncytium
env\Script\activate
uvicorn interface.websocket.websocket:app --reload --port 8081
```
