from sqlalchemy import Table, Column, Integer, String, Text, DateTime
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
