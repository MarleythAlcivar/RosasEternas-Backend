# Rosas Eternas — Backend

API de desarrollo para **Rosas Eternas**, implementada con FastAPI y Uvicorn.

## Endpoints

- `GET /api/health`: confirma disponibilidad de la API.
- `POST /api/capability-events`: recibe metadatos mínimos y seguros de las capacidades nativas de un pedido.

La API aplica límite básico de solicitudes por IP y cabeceras de seguridad. No acepta imágenes, rutas locales ni coordenadas precisas.

## Ejecución local

1. Cree y active un entorno virtual.
2. Instale dependencias: `python -m pip install -r requirements.txt`.
3. Copie `.env.example` a `.env` y ajuste únicamente variables locales.
4. Ejecute: `python -m uvicorn app.main:app --host 0.0.0.0 --port 800 --env-file .env`.

En desarrollo, pruebe `http://127.0.0.1:800/api/health`.

## Seguridad

El archivo `.env` está excluido del control de versiones. Nunca publique tokens, contraseñas, claves privadas ni credenciales de base de datos.
