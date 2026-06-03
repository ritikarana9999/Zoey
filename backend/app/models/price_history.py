from sqlalchemy import Column, Boolean, DateTime, Date, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    store_product_id = Column(UUID(as_uuid=True), ForeignKey("store_products.id"))
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.id"))
    price = Column(Numeric(10, 2), nullable=False)
    unit_price = Column(Numeric(10, 4))
    unit_type = Column(DateTime)
    is_on_sale = Column(Boolean, default=False)
    original_price = Column(Numeric(10, 2))
    captured_at = Column(DateTime, server_default=func.now())
    date_captured = Column(Date, server_default=func.current_date())
