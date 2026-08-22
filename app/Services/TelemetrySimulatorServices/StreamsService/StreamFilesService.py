import asyncio
import json
import logging
from pathlib import Path
from typing import Dict

import aiofiles

from app.Constants.StreamMessages import StreamMessages
from app.Core.config import settings
from app.DTOs.KafkaDTOs import KafkaMessageDTO
from app.DTOs.StreamsDTOs import StartStreamDTO, StopStreamDTO
from app.Interfaces.IKafkaProducerService import IKafkaProducerService
from app.Interfaces.IStreamFilesService import IStreamFilesService
from app.ROSs.StreamsROs import (
    StartStreamErrorResponse,
    StartStreamSuccessResponse,
    StopStreamErrorResponse,
    StopStreamSuccessResponse,
)

logger = logging.getLogger(__name__)


class StreamFilesService(IStreamFilesService):

    def __init__(self, kafka_producer: IKafkaProducerService):
        self._producer = kafka_producer
        self._active_tasks: Dict[str, asyncio.Task] = {}
        self._storage_path = Path(settings.STORAGE_DECODED_PATH)

    async def _stream_file_worker(self, file_name: str, file_path: Path) -> None:
        """Read file line by line and send each frame immediately to Kafka."""
        topic = settings.MAIN_TOPIC_NAME

        try:
            async with aiofiles.open(file_path, mode="r", encoding="utf-8") as f:
                async for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    # Parse single frame
                    frame_data = json.loads(line)

                    #ליאל אני אדבר איתך על זה כבר זה משהו ממש חשוב ובכנווה עשיתי את זה ככה 
                    key = file_name

                    # Send directly to Kafka
                    message = KafkaMessageDTO(
                        topic=topic,
                        value=frame_data,
                        key=key,
                    )
                    await self._producer.send_message(message)

            logger.info(StreamMessages.STREAM_COMPLETED.format(file_name))
        except asyncio.CancelledError:
            logger.info(StreamMessages.STREAM_STOPPED.format(file_name))
            raise
        except Exception as e:
            logger.error(f"Error while streaming file '{file_name}': {e}")
        finally:
            self._active_tasks.pop(file_name, None)

    async def start_stream_file(
        self, request: StartStreamDTO
    ) -> StartStreamSuccessResponse | StartStreamErrorResponse:
        """Start streaming file frames in the background."""
        file_name = request.file_name

        if file_name in self._active_tasks:
            return StartStreamErrorResponse(
                message=StreamMessages.STREAM_ALREADY_RUNNING.format(file_name)
            )

        file_path = self._storage_path / file_name
        if not file_path.exists():
            return StartStreamErrorResponse(
                message=StreamMessages.FILE_NOT_FOUND.format(file_name)
            )

        try:
            task = asyncio.create_task(self._stream_file_worker(file_name, file_path))
            self._active_tasks[file_name] = task

            topic = settings.MAIN_TOPIC_NAME
            return StartStreamSuccessResponse(
                message=StreamMessages.STREAM_STARTED.format(file_name, topic)
            )
        except Exception as e:
            logger.error(f"Failed to start stream for file '{file_name}': {e}")
            return StartStreamErrorResponse(
                message=StreamMessages.INTERNAL_ERROR.format(str(e))
            )

    async def stop_stream_file(
        self, request: StopStreamDTO
    ) -> StopStreamSuccessResponse | StopStreamErrorResponse:
        """Stop an active streaming task."""
        file_name = request.file_name
        task = self._active_tasks.get(file_name)

        if not task or task.done():
            return StopStreamErrorResponse(
                message=StreamMessages.STREAM_NOT_FOUND.format(file_name)
            )

        try:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

            self._active_tasks.pop(file_name, None)
            return StopStreamSuccessResponse(
                message=StreamMessages.STREAM_STOPPED.format(file_name)
            )
        except Exception as e:
            logger.error(f"Failed to stop stream for file '{file_name}': {e}")
            return StopStreamErrorResponse(
                message=StreamMessages.INTERNAL_ERROR.format(str(e))
            )