from fastapi import APIRouter, Depends, File, UploadFile, status

from app.Core.config import settings
from app.dependencies import get_telemetry_files_service
from app.DTOs.DeleteFileDTO import DeleteFileDTO
from app.Interfaces.Itelemetry_files_service import ITelemetryFilesService
from app.Constants.Constants import FastConf

current_version = settings.CURRENT_VERSION
router = APIRouter(
    prefix=FastConf.APP_URL.format(current_version),
    tags=[FastConf.APP_TAG]
)

#--------------Recive and save file--------------------------
@router.post("/files", status_code=status.HTTP_200_OK)
async def recive_klv_file(file: UploadFile = File(...), files_service: ITelemetryFilesService = Depends(get_telemetry_files_service)):   
    return await files_service.Recive_file(file)
#----------------end-----------------------------------------

#-----------------delete file from the service-------------------
@router.delete("/files", status_code=status.HTTP_200_OK)
async def delete_klv_file(dto: DeleteFileDTO, files_service: ITelemetryFilesService = Depends(get_telemetry_files_service)):   
    return await files_service.Delete_file(dto.file_name)
#------------------end---------------------------------------