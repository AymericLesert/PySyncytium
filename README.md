# PySyncytium

## D�marrage de l'API

```
cd PySyncytium
env\Script\activate
python syncytium.py --name api
or
fastapi dev interface\api\api.py
```

## D�marrage du front HTML

```
cd PySyncytium
env\Script\activate
python syncytium.py --name web
or
uvicorn interface.web.web:app --reload --port 8080
```

## D�marrage du serveur WebSocket

```
cd PySyncytium
env\Script\activate
python syncytium.py --name websocket
or
uvicorn interface.websocket.websocket:app --reload --port 8081
```

## D�marrage des tests unitaires

```
cd PySyncytium
env\Script\activate
python -m test.configuration
```

