from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import relationship

from shopapi.db import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    asin = Column(String(32), nullable=True, index=True)
    url = Column(Text, nullable=False)
    title = Column(Text, nullable=True)
    brand = Column(String(255), nullable=True)
    seller = Column(String(255), nullable=True)
    availability = Column(String(128), nullable=True)
    price_amount = Column(Float, nullable=True)
    price_currency = Column(String(8), nullable=True)
    list_price_amount = Column(Float, nullable=True)
    rating = Column(Float, nullable=True)
    review_count = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    feature_bullets = Column(JSON, nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)

    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    specs = relationship("ProductSpec", back_populates="product", cascade="all, delete-orphan")
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")

    def to_dict(self, deep=False):
        data = {
            "id": self.id,
            "asin": self.asin,
            "url": self.url,
            "title": self.title,
            "brand": self.brand,
            "seller": self.seller,
            "availability": self.availability,
            "price_amount": self.price_amount,
            "price_currency": self.price_currency,
            "list_price_amount": self.list_price_amount,
            "rating": self.rating,
            "review_count": self.review_count,
            "description": self.description,
            "feature_bullets": self.feature_bullets or [],
            "fetched_at": self.fetched_at.isoformat() if self.fetched_at else None,
        }
        if deep:
            data["images"] = [img.to_dict() for img in self.images]
            data["specs"] = [s.to_dict() for s in self.specs]
            data["variants"] = [v.to_dict() for v in self.variants]
        return data
