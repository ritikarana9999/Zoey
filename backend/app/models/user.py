from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(300), nullable=False, unique=True)
    name = Column(String(200))
    preferred_store_id = Column(UUID(as_uuid=True), ForeignKey("stores.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
