from datetime import datetime

from pydantic import BaseModel, Field


class MovementCreate(BaseModel):
    product_id: int
    movement_type: str = Field(..., pattern="^(entry|exit|adjustment)$")
    quantity: int = Field(..., gt=0)
    reason: str | None = None


class MovementResponse(BaseModel):
    id: int
    product_id: int
    user_id: int | None = None
    movement_type: str
    quantity: int
    previous_stock: int
    new_stock: int
    reason: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
