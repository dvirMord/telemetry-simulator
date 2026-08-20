from abc import ABC, abstractmethod
from fastapi import UploadFile
from app.ROSs.ReciveFileRos import *

class ITelemetryFilesService(ABC):
    @abstractmethod
    async def Recive_file(self, file: UploadFile) -> FileSuccessResponse | FileErrorResponse:
        pass

    async def Delete_file(self, file_name: str) -> FileSuccessResponse | FileErrorResponse:
        pass