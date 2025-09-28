from fastapi import FastAPI
from app.routers import chat, metrics
from app.database import database, metadata, engine # Importa motor y metadata
import os
import sys

# Importación de CORS (para desarrollo)
from fastapi.middleware.cors import CORSMiddleware 

# --- Configuración de Logging ---
print("--- [DEBUG: main.py] Iniciando configuración de AdGenie Backend API... ---")

app = FastAPI(title="AdGenie Backend API")

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
print("[DEBUG: main.py] CORS Middleware configurado exitosamente.")

# 🛑 SOLUCIÓN AL CICLO DE IMPORTACIÓN: Importar modelos aquí
print("[DEBUG: main.py] Importando modelos ORM para la creación de tablas.")
# Importamos los modelos (asegúrate de que app/models/ existe)
try:
    # 🚨 ¡Ajuste CRÍTICO aquí! Solo importamos los modelos que existen.
    from app.models import users, interactions 
    print("[DEBUG: main.py] Modelos ORM cargados exitosamente.")
except ImportError as e:
    # Esto ahora solo fallará si falta 'users' o 'interactions'
    print(f"[ERROR: main.py] No se pudieron importar los modelos ORM: {e}")
    sys.exit(1) # Detener el servidor si los modelos son inaccesibles


# # Crear tablas SQLite si no existen
# print("[DEBUG: main.py] Intentando crear tablas SQLite si no existen...")
# metadata.create_all(engine)
# print("[DEBUG: main.py] Base de datos y tablas verificadas/creadas.")


# Inclusión de Routers
app.include_router(chat.router)
print("[DEBUG: main.py] Router de Chat incluido.")

app.include_router(metrics.router)
print("[DEBUG: main.py] Router de Métricas incluido.")


@app.on_event("startup")
async def startup():
    print("[DEBUG: STARTUP] Evento 'startup' iniciado.")
    await database.connect()
    print("[DEBUG: STARTUP] Conexión a la base de datos establecida exitosamente.")

@app.on_event("shutdown")
async def shutdown():
    print("[DEBUG: SHUTDOWN] Evento 'shutdown' iniciado.")
    await database.disconnect()
    print("[DEBUG: SHUTDOWN] Desconexión de la base de datos completada. Servidor detenido.")

@app.get("/")
async def root():
    return {"message": "AdGenie Backend Online"}

@app.on_event("startup")
async def startup():
    print("[DEBUG: STARTUP] Evento 'startup' iniciado.")

    # 👈 NUEVA POSICIÓN: Creamos las tablas después de que los modelos
    # se cargaron y antes de conectarse a la BD.
    print("[DEBUG: STARTUP] Creando tablas SQLite si no existen (Ejecución Post-Models).")
    metadata.create_all(engine) 
    print("[DEBUG: STARTUP] Base de datos y tablas verificadas/creadas.")

    await database.connect()
    print("[DEBUG: STARTUP] Conexión a la base de datos establecida exitosamente.")

print("--- [DEBUG: main.py] Configuración inicial de FastAPI completada. ---")