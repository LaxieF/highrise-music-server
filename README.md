# Highrise Music Server API

Servidor independiente para la transmisión de audio en salas de Highrise.

## Endpoints:
- `GET /` -> Estado del servidor.
- `POST /play` -> Recibe `{"query": "cancion"}` y devuelve la URL del flujo de audio directo.
