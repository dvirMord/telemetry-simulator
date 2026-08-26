import sys
import os
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.Core.logger import setup_logger
setup_logger()

logger = logging.getLogger(__name__)

from app.Core.config import settings
from app.Constants.Constants import FastConf
from app.Controllers.TelemetryFilesController import router as files_router
from app.Controllers.StreamsController import router as streams_controller
from app.dependencies import get_kafka_producer, get_db_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ------------------ STARTUP ------------------
    try:
        db_manager = get_db_manager()
        await db_manager.start_connection()

        kafka_producer = get_kafka_producer()
        await kafka_producer.start()

        logger.info("Application startup completed successfully")

        yield

    except Exception:
        logger.exception("Application startup failed")
        raise

    finally:
        # ------------------ SHUTDOWN ------------------
        logger.info("Shutting down application...")


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