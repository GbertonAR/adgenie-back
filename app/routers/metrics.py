# app/routers/metrics.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.interactions import ChatInteraction
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter(
    prefix="/metrics",
    tags=["Metrics"],
)

# 1. Modelo de Respuesta para la Consistencia
class MetricsSummary(BaseModel):
    """Estructura de la respuesta del resumen de métricas."""
    total_interactions: int
    context_distribution: Dict[str, int]
    # Puedes añadir más campos (ej: top_users, latest_interaction_date)

# 2. Endpoint Principal: /metrics/summary
@router.get("/summary", response_model=MetricsSummary)
def get_metrics_summary(db: Session = Depends(get_db)):
    """
    Calcula el resumen de las interacciones del chat, incluyendo el total 
    y la distribución por contexto (MARKETING, TECH, DEFAULT).
    """
    
    # 1. Total de Interacciones
    total_interactions = db.query(ChatInteraction).count()

    # 2. Distribución por Contexto
    # Usamos func.count() y func.group_by() para contar las filas por el valor de la columna 'context'.
    context_results = (
        db.query(
            ChatInteraction.context, 
            func.count(ChatInteraction.context)
        )
        .group_by(ChatInteraction.context)
        .all()
    )

    # 3. Formatear la Distribución
    # Convertimos la lista de tuplas [(contexto, conteo), ...] a un diccionario {contexto: conteo}
    context_distribution = {context: count for context, count in context_results}

    print(f"[DEBUG: METRICS] Interacciones totales: {total_interactions}")
    print(f"[DEBUG: METRICS] Distribución de contextos: {context_distribution}")
    
    # 4. Retornar el Modelo de Respuesta
    return MetricsSummary(
        total_interactions=total_interactions,
        context_distribution=context_distribution
    )