from pydantic import BaseModel
#-----------Ros for start stream ------------
class StartStreamSuccessResponse(BaseModel):
  success: bool = True
  message: str

class StartStreamErrorResponse(BaseModel):
  success: bool = False
  message: str
#----------------------------------------------

#-----------Ros for stop stream ------------
class StopStreamSuccessResponse(BaseModel):
  success: bool = True
  message: str

class StopStreamErrorResponse(BaseModel):
  success: bool = False
  message: str
#----------------------------------------------