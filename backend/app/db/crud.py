from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Product


def get_product(db: Session, product_id: int) -> Product | None:
    return db.scalar(select(Product).where(Product.id == product_id))
