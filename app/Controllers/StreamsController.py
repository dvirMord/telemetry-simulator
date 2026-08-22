from fastapi import APIRouter, Depends, status
from app.Interfaces.IStreamFilesService import IStreamFilesService
from app.DTOs.StreamsDTOs import StartStreamDTO, StopStreamDTO
from app.ROSs.StreamsROs import (
    StartStreamSuccessResponse,
    StartStreamErrorResponse,
    StopStreamSuccessResponse,
    StopStreamErrorResponse,
)
from app.dependencies import get_stream_files_service
from app.Core.config import settings

currnetVersion = settings.CURRENT_VERSION
router = APIRouter( prefix=f"/api/{currnetVersion}/ts", tags=["Telemetry Stream"])


@router.post(
    "/start",
    response_model=StartStreamSuccessResponse | StartStreamErrorResponse,
    status_code=status.HTTP_200_OK,
    summary="Start streaming telemetry file to Kafka"
)
async def start_stream(
    request: StartStreamDTO,
    stream_service: IStreamFilesService = Depends(get_stream_files_service),
):
    """Start reading and publishing telemetry file frames to Kafka."""
    return await stream_service.start_stream_file(request)


@router.post(
    "/stop",
    response_model=StopStreamSuccessResponse | StopStreamErrorResponse,
    status_code=status.HTTP_200_OK,
    summary="Stop streaming telemetry file"
)
async def stop_stream(
    request: StopStreamDTO,
    stream_service: IStreamFilesService = Depends(get_stream_files_service),
):
    """Cancel an ongoing streaming task."""
    return await stream_service.stop_stream_file(request)