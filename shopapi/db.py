import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


DB_URL = os.environ.get("SHOP_DB_URL", "sqlite:///shop.db")

engine = create_engine(DB_URL, connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
Base = declarative_base()


def init_db():
    from shopapi.models.product import Product
    from shopapi.models.image import ProductImage
    from shopapi.models.spec import ProductSpec
    from shopapi.models.variant import ProductVariant

    Base.metadata.create_all(bind=engine)


def reset_db():
    from shopapi.models.product import Product
    from shopapi.models.image import ProductImage
    from shopapi.models.spec import ProductSpec
    from shopapi.models.variant import ProductVariant

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def get_session():
    return SessionLocal()
