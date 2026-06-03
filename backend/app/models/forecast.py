from sqlalchemy import Column, String, DateTime, Date, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base


class Forecast(Base):
    __tablename__ = "forecasts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.id"))
    forecast_date = Column(Date, nullable=False)
    predicted_price = Column(Numeric(10, 2), nullable=False)
    lower_bound = Column(Numeric(10, 2))
    upper_bound = Column(Numeric(10, 2))
    model_name = Column(String(100))
    confidence = Column(Numeric(5, 4))
    created_at = Column(DateTime, server_default=func.now())
