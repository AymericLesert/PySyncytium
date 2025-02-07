# PySyncytium

## Démarrage de l'API

```
cd PySyncytium
env\Script\activate
fastapi dev interface\api\api.py
```

## Démarrage du front HTML

```
cd PySyncytium
env\Script\activate
uvicorn interface.web.web:app --reload --port 8080
```

## Démarrage du serveur WebSocket

```
cd PySyncytium
env\Script\activate
uvicorn interface.websocket.websocket:app --reload --port 8081
```
