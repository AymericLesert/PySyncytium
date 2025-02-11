# PySyncytium

## D�marrage de l'API

```
cd PySyncytium
env\Script\activate
python api.py
or
fastapi dev interface\api\api.py
```

## D�marrage du front HTML

```
cd PySyncytium
env\Script\activate
python web.py
or
uvicorn interface.web.web:app --reload --port 8080
```

## D�marrage du serveur WebSocket

```
cd PySyncytium
env\Script\activate
python websocket.py
or
uvicorn interface.websocket.websocket:app --reload --port 8081
```
