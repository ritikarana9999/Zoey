from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    recommended_product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    similarity_score = Column(Numeric(5, 4))
    price_savings = Column(Numeric(10, 2))
    reason = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())
