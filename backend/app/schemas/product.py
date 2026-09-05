from pydantic import BaseModel, ConfigDict


class ProductCreate(BaseModel):
    name: str
    brand: str | None = None
    category: str | None = None
    description: str | None = None


class ProductRead(ProductCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
