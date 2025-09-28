# app/models/users.py - Versión Final Corregida

from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base 

class User(Base):
    """
    Modelo ORM para la tabla 'users'. Almacena los usuarios únicos basados 
    en su session_id.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, nullable=False, index=True)
    name = Column(String)
    created_at = Column(DateTime, default=func.now())

    # 👈 ¡LA PROPIEDAD QUE FALTABA Y CAUSÓ EL ERROR!
    # Define la colección de interacciones asociadas a este usuario.
    interactions = relationship(
        "ChatInteraction", 
        back_populates="user",
        cascade="all, delete-orphan" # Permite eliminar interacciones si el usuario se borra
    )