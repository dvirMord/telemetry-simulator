from abc import ABC, abstractmethod
from app.DTOs.StreamsDTOs import *
from app.ROSs.StreamsROs import *

class IStreamFilesService(ABC):
    @abstractmethod
    async def start_stream_file(self, requset: StartStreamDTO) -> StartStreamSuccessResponse | StartStreamErrorResponse:
        pass

    @abstractmethod
    async def stop_stream_file(self, requset: StopStreamDTO) -> StopStreamSuccessResponse | StopStreamErrorResponse:
        pass