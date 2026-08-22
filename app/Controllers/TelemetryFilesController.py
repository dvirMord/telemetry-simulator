from fastapi import APIRouter, UploadFile, File, Depends
from app.Interfaces.Itelemetry_files_service import ITelemetryFilesService
from app.dependencies import get_telemetry_files_service
from app.DTOs.DeleteFileDTO import DeleteFileDTO
from app.Core.config import settings
current_version = settings.CURRENT_VERSION
router = APIRouter(
    prefix=f"/api/{current_version}/ts",
    tags=["Telemetry files"]
)

#--------------Recive and save file--------------------------
@router.post("/files")
async def recive_klv_file(file: UploadFile = File(...), files_service: ITelemetryFilesService = Depends(get_telemetry_files_service)):
    return await files_service.Recive_file(file)
#----------------end-----------------------------------------

#-----------------delete file from the service-------------------
@router.delete("/files")
async def delete_klv_file(dto: DeleteFileDTO, files_service: ITelemetryFilesService = Depends(get_telemetry_files_service)):
    return await files_service.Delete_file(dto.file_name)
#------------------end---------------------------------------