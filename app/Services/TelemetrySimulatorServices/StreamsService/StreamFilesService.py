import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Set

import aiofiles
from app.Interfaces.IDBManager import IDBManager
from app.Constants.StreamMessages import StreamMessages
from app.DTOs.DBDTOs import AddChannelDbDTO, FileType
from app.Constants.Constants import KafkaConst
from app.Core.config import settings
from app.DTOs.DBDTOs import AddChannelDbDTO, FileType
from app.DTOs.KafkaDTOs import KafkaMessageDTO
from app.DTOs.StreamsDTOs import StartStreamDTO, StopStreamDTO
from app.Interfaces.IDBManager import IDBManager
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

    def __init__(self, kafka_producer: IKafkaProducerService, db_manager: IDBManager):
        self._producer = kafka_producer
        self._db_manager = db_manager
        self._active_tasks: Dict[str, asyncio.Task] = {}
        self._file_to_partition: Dict[str, int] = {}
        self._storage_path = Path(settings.STORAGE_DECODED_PATH)

    def _get_partition(self, file_name: str) -> int:
        """Find the lowest available partition index (0-9)."""
        if file_name in self._file_to_partition:
            return self._file_to_partition[file_name]
        used_partitions: Set[int] = set(self._file_to_partition.values())
        for partition_id in range(KafkaConst.MAX_PARTITIONS):
            if partition_id not in used_partitions:
                self._file_to_partition[file_name] = partition_id
                return partition_id
        raise RuntimeError(StreamMessages.ALL_PARTITIONS_USED)

    async def _stream_file_worker(self, file_name: str, file_path: Path, partition: int) -> None:
        """Read file line by line and route directly to the designated partition."""
        topic = settings.MAIN_TOPIC_NAME

        try:
            async with aiofiles.open(file_path, mode="r", encoding="utf-8") as f:
                async for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    frame_data = json.loads(line)
                    drone_id = frame_data.get(StreamMessages.DRONE_ID_KEY, file_name)

                    message = KafkaMessageDTO(
                        topic=topic,
                        value=frame_data,
                        key=drone_id,
                        partition=partition,
                    )
                    await self._producer.send_message(message)

            logger.info(StreamMessages.STREAM_COMPLETED.format(file_name))
        except asyncio.CancelledError:
            logger.info(StreamMessages.STREAM_STOPPED.format(file_name))
            raise
        except Exception as e:
            logger.error(StreamMessages.ERROR_STREAMING, file_name, e)
        finally:
            self._active_tasks.pop(file_name, None)
            self._file_to_partition.pop(file_name, None)

    async def start_stream_file(self, request: StartStreamDTO) -> StartStreamSuccessResponse | StartStreamErrorResponse:
            file_name = request.file_name

            if file_name in self._active_tasks:
                return StartStreamErrorResponse(message=StreamMessages.STREAM_ALREADY_RUNNING.format(file_name))

            file_path = self._storage_path / file_name
            if not file_path.exists():
                return StartStreamErrorResponse(
                    message=StreamMessages.FILE_NOT_FOUND.format(file_name))

        try:
            partition = self._get_partition(file_name)

            source_file_id = await self._db_manager.get_source_file_id(str(file_path))
            add_channel_dto = AddChannelDbDTO(
                source_file_id=source_file_id,
                kafka_partition=partition,
                file_type=FileType.DECODED,
            )
            await self._db_manager.add_channel(add_channel_dto)

            task = asyncio.create_task(self._stream_file_worker(file_name, file_path, partition))
            self._active_tasks[file_name] = task

            return StartStreamSuccessResponse(
                message=StreamMessages.STREAM_SUCCES.format(file_name, partition)
            )
        except Exception as e:
            self._file_to_partition.pop(file_name, None)
            logger.error(StreamMessages.FAILD_TO_START.format(file_name, e))
            return StartStreamErrorResponse(
                message=StreamMessages.INTERNAL_ERROR.format(str(e))
            )

    async def stop_stream_file(
        self, request: StopStreamDTO
    ) -> StopStreamSuccessResponse | StopStreamErrorResponse:
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
            return StopStreamSuccessResponse(
                message=StreamMessages.STREAM_STOPPED.format(file_name)
            )
        except Exception as e:
            logger.error(StreamMessages.FAILD_TO_STOP_STREAM.format(file_name, e))
            return StopStreamErrorResponse(
                message=StreamMessages.INTERNAL_ERROR.format(str(e))
            )