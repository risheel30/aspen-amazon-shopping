from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from shopapi.db import Base


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    kind = Column(String(32), nullable=False)
    value = Column(String(255), nullable=False)
    asin = Column(String(32), nullable=True)

    product = relationship("Product", back_populates="variants")

    def to_dict(self):
        return {"id": self.id, "kind": self.kind, "value": self.value, "asin": self.asin}
