from pydantic import BaseModel, Field
from enum import Enum

class Constants:
    BIN_STRING = 'klv-bin file.'
    DECODE_FILE = 'decoded-txt file'
class FileType(Enum):
    BIN = Constants.BIN_STRING
    DECODED = Constants.DECODE_FILE

class AddFileDbDTO(BaseModel):
    path: str = Field(...)
    size: int = Field(...)
    file_type: FileType = Field(...)

class RemoveFileDbDTO(BaseModel):
    path: str = Field(...)
    
class AddChannelDbDTO(BaseModel):
    source_file_id: int = Field(...)
    kafka_partition: int = Field(..., ge=0, le=9)
    file_type: FileType = Field(...)