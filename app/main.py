import sys
import os
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.Core.config import settings
from app.Constants.Constants import FastConf
from app.Controllers.TelemetryFilesController import router as files_router
from app.Controllers.StreamsController import router as streams_controller
from app.dependencies import get_kafka_producer


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize and connect Kafka Producer
    producer = get_kafka_producer()
    await producer.start()
    yield
    # Shutdown: Close Kafka Producer connection gracefully
    await producer.stop()


app = FastAPI(
    title=FastConf.TITLE,
    description=FastConf.DESCRIPTION,
    version=settings.CURRENT_VERSION,
    lifespan=lifespan,
)

app.include_router(files_router)
app.include_router(streams_controller)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.IP, port=settings.PORT, reload=True)