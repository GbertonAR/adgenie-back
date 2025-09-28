from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.users import User
from app.models.interactions import ChatInteraction
from pydantic import BaseModel
import datetime
import sys
import os
#import openai # Necesitas instalar la librería 'openai' (pip install openai)

from dotenv import load_dotenv

load_dotenv()
#from openai import OpenAI
import openai
# --- CONFIGURACIÓN DE AZURE (DEBE USAR VARIABLES DE ENTORNO) ---
# Importante: Estas variables DEBEN estar definidas en su entorno (.env o similar)
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_DEPLOYMENT_NAME = "gpt-5-chat-optiFoodAI-1" # O el nombre de su implementación en Azure

# Configuración del cliente de OpenAI para Azure
try:
    print("Iniciando configuración del cliente de Azure OpenAI...")
    print(f"AZURE_ENDPOINT: {AZURE_ENDPOINT}")
    print(f"AZURE_API_KEY: {AZURE_API_KEY}")
    if AZURE_ENDPOINT and AZURE_API_KEY:
        openai_client = openai.AzureOpenAI(
            azure_endpoint=AZURE_ENDPOINT,
            api_key=AZURE_API_KEY,
            api_version="2025-01-01-preview" # Asegúrese de usar una versión compatible
        )
        print("Cliente de Azure OpenAI configurado correctamente.")
    else:
        openai_client = None
        print("ADVERTENCIA: Variables de entorno de Azure no cargadas. Usando lógica de prueba.")

except Exception as e:
    openai_client = None
    print(f"ERROR: Fallo al inicializar el cliente de Azure OpenAI: {e}")

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)

class MessageRequest(BaseModel):
    message: str
    session_id: str

# ----------------------------------------------------------------
# --- NUEVA LÓGICA DE AZURE AI -----------------------------------
# ----------------------------------------------------------------

SYSTEM_PROMPT = """
Eres AdGenie, un experto en marketing digital y optimización de campañas (Google Ads, Meta Ads). 
Tu objetivo es responder preguntas con conocimiento técnico y clasificar la intención de la consulta del usuario.
Tu respuesta DEBE ser un objeto JSON con dos campos:
1. "reply": La respuesta experta para el usuario (máx. 150 palabras).
2. "context": La clasificación de la consulta. Elige uno de estos valores: 
   - MARKETING_OPTIMIZATION (si pregunta por CTR, CPC, pujas, audiencias).
   - TECH_STACK (si pregunta por Python, FastAPI, React, Azure).
   - GENERAL_INQUIRY (para saludos o preguntas no relacionadas con marketing/tech).
"""

def call_azure_ai(message: str) -> tuple[str, str]:
    """Llama a la API de Azure y parsea la respuesta JSON."""
    if not openai_client:
        # Si Azure no está configurado, vuelve a la lógica de prueba (fallback)
        print("[DEBUG: AZURE] Cliente no configurado. Usando Fallback de prueba.")
        return get_ai_response_fallback(message)

    try:
        print(f"[DEBUG: AZURE_API_CALL] Enviando mensaje a Azure: '{message}'")
        print(f"[DEBUG: AZURE_API_CALL] Usando endpoint: {AZURE_ENDPOINT}")
        print(f"[DEBUG: AZURE_API_CALL] Usando deployment: {AZURE_DEPLOYMENT_NAME}")
        print(f"SYSTEM_PROMPT: {SYSTEM_PROMPT} ")
        response = openai_client.chat.completions.create(
            model=AZURE_DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message},
            ],
            # Importante: Pedimos el formato JSON
            response_format={"type": "json_object"}
        )
        
        # El modelo de Azure devuelve un string JSON
        json_output = response.choices[0].message.content
        
        # 1. Parsear JSON
        import json
        data = json.loads(json_output)
        
        reply = data.get("reply", "Lo siento, la IA no pudo generar una respuesta válida.")
        context = data.get("context", "DEFAULT_PROCESSING")
        
        return reply, context

    except Exception as e:
        print(f"[ERROR: AZURE_API_CALL] Fallo en la llamada a Azure: {e}")
        # En caso de error de API, volvemos a la lógica de prueba
        return get_ai_response_fallback(message)


# Lógica de prueba anterior (se convierte en fallback)
def get_ai_response_fallback(message: str) -> tuple[str, str]:
    # Placeholder para la lógica contextual
    marketing_keywords = ["optimizar", "ctr", "cpc", "campaña", "métricas"]
    tech_keywords = ["python", "fastapi", "react", "vite", "azure"]
    off_topic_keywords = ["capital", "tiempo", "edad", "quién eres"]
    
    if any(keyword in message.lower() for keyword in marketing_keywords):
        return "¡Excelente! Hemos detectado una consulta sobre optimización de campañas. Estamos listos para analizar sus métricas.", "MARKETING_OPTIMIZATION"
    if any(keyword in message.lower() for keyword in tech_keywords):
        return "Claro, nuestra pila tecnológica está basada en Python/FastAPI y React/Vite, todo escalado en Azure.", "TECH_STACK"
    if any(keyword in message.lower() for keyword in off_topic_keywords):
        return "Soy AdGenie, tu asistente de campañas. Mi foco es el marketing digital. ¿En qué puedo ayudar?", "GENERAL_INQUIRY"

    return f"He recibido tu solicitud: '{message}'. Estoy buscando la mejor decisión de un experto. ¡Gracias por usar AdGenie!", "DEFAULT_PROCESSING"


# Reemplazamos la función original por la que llama a Azure
def get_ai_response(message: str) -> tuple[str, str]:
    return call_azure_ai(message)

# ----------------------------------------------------------------
# --- ENDPOINT DE CHAT (Se mantiene sin cambios) ------------------
# ----------------------------------------------------------------

@router.post("/message")
async def send_message(req: MessageRequest, db: Session = Depends(get_db)):
    # ... (El resto del código del router permanece igual, usando la nueva get_ai_response)
    print(f"[DEBUG: /chat/message] Recibida nueva solicitud. Session ID: '{req.session_id}'")
    
    try:
        # 1. Buscar o Crear Usuario (Transacción atómica)
        user = db.query(User).filter(User.session_id == req.session_id).first()
        
        if not user:
            user = User(session_id=req.session_id, name="Anonymous")
            db.add(user)
            db.flush()
            print(f"[DEBUG: DB_USER] Nuevo usuario creado con ID: {user.id}")
        else:
            print(f"[DEBUG: DB_USER] Usuario existente encontrado con ID: {user.id}")

        # 2. Generar Respuesta (AQUÍ se llama a la nueva lógica de Azure)
        bot_reply, context = get_ai_response(req.message)
        print(f"[DEBUG: AI_LOGIC] Contexto de respuesta detectado: '{context}'")

        # 3. Guardar Interacciones
        user_interaction = ChatInteraction(
            user_id=user.id, 
            context=context, 
            message_type="USER", 
            message_text=req.message
        )
        db.add(user_interaction)
        
        bot_interaction = ChatInteraction(
            user_id=user.id, 
            context=context, 
            message_type="BOT", 
            message_text=bot_reply
        )
        db.add(bot_interaction)

        # 4. Commit Final
        db.commit()
        print("[DEBUG: DB_PERSIST] Transacción completa: Mensajes guardados.")
        
        # 5. Respuesta
        return {"reply": bot_reply}

    except Exception as e:
        db.rollback()
        print(f"[ERROR: DB_TXN_FAILED] Fallo de transacción. Rollback ejecutado: {e}", file=sys.stderr)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al procesar la solicitud de chat."
        ) from e