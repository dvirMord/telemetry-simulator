from pydantic import BaseModel 

class DeleteFileDTO(BaseModel):
    file_name: str = str(...)