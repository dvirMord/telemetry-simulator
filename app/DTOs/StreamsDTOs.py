from pydantic import BaseModel 

class StartStreamDTO(BaseModel):
    file_name: str = str(...)

class StopStreamDTO(BaseModel):
    file_name: str = str(...)