from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from shopapi.db import Base


class ProductSpec(Base):
    __tablename__ = "product_specs"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    key = Column(String(255), nullable=False)
    value = Column(Text, nullable=True)

    product = relationship("Product", back_populates="specs")

    def to_dict(self):
        return {"id": self.id, "key": self.key, "value": self.value}
