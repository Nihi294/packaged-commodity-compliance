from pydantic import BaseModel, ConfigDict


class RuleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    description: str | None = None
    is_active: bool


class RuleResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    scan_id: int
    rule_id: int
    passed: bool
    details: dict | None = None
