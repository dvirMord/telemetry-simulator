import sys
import os
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

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
    db_manager = get_db_manager()
    kafka_producer = get_kafka_producer()

    # ------------------ STARTUP ------------------
    try:
        await db_manager.start_connection()
        await kafka_producer.start()

        logger.info(FastConf.STARTUP_COMPLETED)

    except Exception:
        logger.exception(FastConf.STARTUP_FAILED)
        raise

    # Application runs here
    yield

    # ------------------ SHUTDOWN ------------------
    logger.info(FastConf.SHUTDOWN_STARTED)

    try:
        await kafka_producer.stop()
        logger.info(FastConf.KAFKA_PRODUCER_STOPPED)
    except Exception:
        logger.exception(FastConf.KAFKA_PRODUCER_STOP_FAILED)

    try:
        await db_manager.close_connection()
        logger.info(FastConf.DATABASE_CONNECTION_CLOSED)
    except Exception:
        logger.exception(FastConf.DATABASE_CONNECTION_CLOSE_FAILED)

    logger.info(FastConf.SHUTDOWN_COMPLETED)


app = FastAPI(
    title=FastConf.TITLE,
    description=FastConf.DESCRIPTION,
    version=settings.CURRENT_VERSION,
    lifespan=lifespan,
)

app.include_router(files_router)
app.include_router(streams_controller)


if __name__ == "__main__":
    uvicorn.run(
        FastConf.APP_MODULE,
        host=settings.IP,
        port=settings.PORT,
        reload=False,
    )