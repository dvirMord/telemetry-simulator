from fastapi import APIRouter, UploadFile, File, Depends
from app.Services.TelemetrySimulatorServices.Itelemetry_files_service import ITelemetryFilesService
from app.dependencies import get_telemetry_service
from app.DTOs.DeleteFileDTO import DeleteFileDTO
router = APIRouter(
    prefix="/api/v1.0/ts",
    tags=["Telemetry files"]
)

#--------------Recive and save file--------------------------
@router.post("/files")
async def recive_klv_file(file: UploadFile = File(...), files_service: ITelemetryFilesService = Depends(get_telemetry_service)):
    return await files_service.Recive_file(file)
#----------------end-----------------------------------------

#-----------------delete file from the service-------------------
@router.delete("/files")
async def delete_klv_file(dto: DeleteFileDTO, files_service: ITelemetryFilesService = Depends(get_telemetry_service)):
    return await files_service.Delete_file(dto.file_name)
#------------------end---------------------------------------