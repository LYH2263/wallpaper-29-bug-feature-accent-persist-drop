from pydantic import BaseModel, Field


class EstimateRequest(BaseModel):
    wall_id: int
    roll_id: int
    save: bool = False
    note: str = ""
    feature_width: float = Field(0.0, ge=0)
    feature_height: float = Field(0.0, ge=0)
