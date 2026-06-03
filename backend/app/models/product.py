from sqlalchemy import Column, String, Boolean, DateTime, Text, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(500), nullable=False)
    brand = Column(String(200))
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"))
    barcode = Column(String(50))
    description = Column(Text)
    weight_volume = Column(String(100))
    weight_grams = Column(Numeric(10, 2))
    image_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class StoreProduct(Base):
    __tablename__ = "store_products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.id"))
    store_sku = Column(String(200))
    store_url = Column(String(500))
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (UniqueConstraint("product_id", "store_id"),)
