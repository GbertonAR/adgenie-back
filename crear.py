import os
import sqlite3

# Ruta base del proyecto
base_path = r"E:\GBerton2025\Desarrollos\AdGenie"

# Estructura de directorios y archivos
structure = {
    "backend": {
        "app": {
            "routers": {
                "chat.py": """from fastapi import APIRouter
from app.database import database, interactions

router = APIRouter(prefix="/chat", tags=["chat"])

@router.get("/ping")
async def ping():
    return {"message": "Chat router online"}

@router.post("/message")
async def message(user_id: int, text: str):
    # Simulación de respuesta
    response = f"Respuesta simulada a '{text}'"
    
    # Guardar interacción en DB
    query = interactions.insert().values(
        user_id=user_id,
        campaign_id=None,
        message=text,
        response=response
    )
    await database.execute(query)
    
    return {"user_id": user_id, "response": response}
""",
                "metrics.py": """from fastapi import APIRouter

router = APIRouter(prefix="/metrics", tags=["metrics"])

@router.get("/status")
async def status():
    return {"status": "OK", "uptime": "0h 5m"}
"""
            },
            "services": {
                "__init__.py": "# Servicios auxiliares (scoring, integraciones, NLP)"
            },
            "main.py": """from fastapi import FastAPI
from app.routers import chat, metrics
from app.database import database, metadata, engine
import os

app = FastAPI(title="AdGenie Backend API")

# Crear tablas SQLite si no existen
metadata.create_all(engine)

app.include_router(chat.router)
app.include_router(metrics.router)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/")
async def root():
    return {"message": "AdGenie Backend Online"}
""",
            "models.py": """from sqlalchemy import Table, Column, Integer, String, Text, DateTime
from app.database import metadata
import datetime

users = Table(
    "users", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("email", String, nullable=False, unique=True),
    Column("created_at", DateTime, default=datetime.datetime.utcnow)
)

campaigns = Table(
    "campaigns", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("budget", Integer),
    Column("status", String, default="draft"),
    Column("created_at", DateTime, default=datetime.datetime.utcnow)
)

interactions = Table(
    "interactions", metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer),
    Column("campaign_id", Integer),
    Column("message", Text),
    Column("response", Text),
    Column("timestamp", DateTime, default=datetime.datetime.utcnow)
)
""",
            "database.py": """from sqlalchemy import create_engine, MetaData, Table
from databases import Database

DATABASE_URL = "sqlite:///./db/adgenie.db"

database = Database(DATABASE_URL)
metadata = MetaData()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Importar tablas
from app.models import users, campaigns, interactions
"""
        },
        "requirements.txt": """fastapi
uvicorn
pydantic
sqlalchemy
databases[sqlite]
python-dotenv
requests
openai
"""
    },
    "frontend": {
        "src": {
            "components": {
                "Header.jsx": """import React from 'react'

export default function Header() {
    return <header className="p-4 bg-accent text-white font-bold">AdGenie Chatbot</header>
}"""
            },
            "pages": {
                "Home.jsx": """import React from 'react'

export default function Home() {
    return <div className="p-8">Bienvenido a AdGenie. Aquí irán las métricas y chat.</div>
}"""
            },
            "styles": {},
            "App.jsx": """import React from 'react'
import Header from './components/Header'
import Home from './pages/Home'

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-r from-primary to-secondary text-white">
      <Header />
      <Home />
    </div>
  )
}

export default App
""",
            "index.jsx": """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import { setup } from 'twind'

setup({
  theme: {
    extend: {
      colors: {
        primary: 'linear-gradient(90deg, #6A0DAD, #FF00FF)',
        secondary: 'linear-gradient(90deg, #00FFFF, #0000FF)',
        accent: '#FF2400',
      }
    }
  }
})

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
"""
        },
        "package.json": """{
  "name": "adgenie-frontend",
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "twind": "^1.2.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.0.0"
  }
}
"""
    },
    "db": {
        "adgenie.db": ""  # base SQLite vacía
    },
    "README.md": "# Proyecto AdGenie\nChatbot para atención de campañas publicitarias.\n\nEstructura lista para ejecutar backend y frontend localmente."
}

# Función para crear estructura de directorios y archivos
def create_structure(base, struct):
    for name, content in struct.items():
        path = os.path.join(base, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

# Crear estructura
create_structure(base_path, structure)
print(f"Estructura completa de AdGenie creada en {base_path}")

# Inicializar SQLite con datos de prueba
db_path = os.path.join(base_path, "db", "adgenie.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Crear tablas si no existen
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS campaigns (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    budget INTEGER,
    status TEXT DEFAULT 'draft',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS interactions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    campaign_id INTEGER,
    message TEXT,
    response TEXT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
);
""")

# Insertar datos de prueba
cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (1, 'Test User', 'test@example.com')")
cursor.execute("INSERT OR IGNORE INTO campaigns (id, name, budget, status) VALUES (1, 'Campaña Demo', 1000, 'active')")

conn.commit()
conn.close()
print("Base de datos SQLite inicializada con datos de prueba.")
