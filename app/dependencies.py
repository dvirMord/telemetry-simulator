# app/dependencies.py
from app.Interfaces.Itelemetry_files_service import ITelemetryFilesService
from app.Services.TelemetrySimulatorServices.Telemetry_file_service import TelemetryFilesService

def get_telemetry_service() -> ITelemetryFilesService:
    return TelemetryFilesService()