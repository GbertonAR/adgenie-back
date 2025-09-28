# app/database.py

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from databases import Database
import os

# --- Configuración Táctica: Nuevo nombre de DB para evitar bloqueos ---
DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'db')
os.makedirs(DB_DIR, exist_ok=True)
DATABASE_FILE = "adgenie_v3.db" # 👈 Nombre de archivo nuevo
SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(DB_DIR, DATABASE_FILE)}"

# --- Configuración Asíncrona (para FastAPI) ---
database = Database(SQLALCHEMY_DATABASE_URL)

# --- Configuración Síncrona (para SQLAlchemy ORM y creación de tablas) ---
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False} # Requerido para SQLite con múltiples hilos
)

# Base Declarativa (donde los modelos heredarán)
Base = declarative_base()
metadata = Base.metadata

# SessionLocal (Dependencia para inyectar la sesión síncrona en el router)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependencia para FastAPI (manejo de sesión síncrona)
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback() # Garantiza el rollback en caso de error
        print(f"[ERROR: get_db] Excepción durante la solicitud: {e}")
        raise
    finally:
        db.close() # Garantiza el cierre de la sesión