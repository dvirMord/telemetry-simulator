from pydantic import BaseModel, Field


class StartStreamDTO(BaseModel):
    sim_id: int = Field(..., alias="simId", gt=0)

    class Config:
        populate_by_name = True


class StopStreamDTO(BaseModel):
    sim_id: int = Field(..., alias="simId", gt=0)

    class Config:
        populate_by_name = True