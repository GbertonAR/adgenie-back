# app/models/interactions.py - Versión FINAL y COMPLETA

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base 

print("--- [DEBUG: interactions.py] Modelo ChatInteraction cargado exitosamente. ---")

class ChatInteraction(Base):
    """
    Modelo ORM para la tabla 'chat_interactions'. 
    """
    __tablename__ = "chat_interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Columnas de Lógica del Chat
    context = Column(String, nullable=True, default="DEFAULT_PROCESSING")
    message_type = Column(String, nullable=False)
    message_text = Column(String)
    created_at = Column(DateTime, default=func.now())
    
    # 👈 ¡LA PROPIEDAD QUE FALTABA Y CAUSÓ ESTE ERROR!
    # Define la relación de muchos a uno: muchas interacciones a un solo usuario.
    # El 'back_populates' conecta con la propiedad 'interactions' definida en User.
    user = relationship("User", back_populates="interactions")