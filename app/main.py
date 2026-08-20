import sys
import os
import uvicorn
from fastapi import FastAPI
from app.Core.config import settings

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.Controllers.TelemetryFilesController import router as telemetry_router

app = FastAPI(
    title="Telemetry Simulator API",
    description="API for receiving and managing telemetry files",
    version="1.0.0"
)

app.include_router(telemetry_router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.IP, port=settings.PORT, reload=True)