from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    scan_id: int
    user_id: int | None = None
    file_path: str | None = None
    status: str
    created_at: datetime
