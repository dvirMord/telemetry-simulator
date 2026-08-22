from pydantic import BaseModel
#-----------Ros for Recive and save file------------
class FileSuccessResponse(BaseModel):
  success: bool = True
  message: str

class FileErrorResponse(BaseModel):
  success: bool = False
  message: str
#----------------------------------------------