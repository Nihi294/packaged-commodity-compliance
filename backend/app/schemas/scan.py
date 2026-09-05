from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ScanCreate(BaseModel):
    product_id: int | None = None


class ScanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int | None = None
    product_id: int | None = None
    status: str
    created_at: datetime
