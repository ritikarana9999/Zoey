from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
from app.database import Base


class Basket(Base):
    __tablename__ = "baskets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    name = Column(String(200))
    items = Column(JSONB, nullable=False, default=list)
    optimization_result = Column(JSONB, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
