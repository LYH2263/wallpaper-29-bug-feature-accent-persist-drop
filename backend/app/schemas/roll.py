from pydantic import BaseModel, Field


class RollWidthUpdate(BaseModel):
    width: float = Field(..., gt=0)
