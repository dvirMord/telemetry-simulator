from pydantic import BaseModel
#-----------Ros for Recive and save file------------
class FileSuccessResponse(BaseModel):
  success: bool = True
  message: str

class FileSuccessUploadResponse(BaseModel):
  success: bool = True
  message: str
  decodedId: int 

class FileErrorResponse(BaseModel):
  success: bool = False
  message: str
#----------------------------------------------