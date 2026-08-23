import logging
import aiosqlite
from typing import Optional, List, Dict, Any
from app.Interfaces.IDBManager import IDBManager
from app.DTOs.DBDTOs import AddFileDbDTO, AddChannelDbDTO, RemoveFileDbDTO
from app.Constants.DbConstants import InitScript, DbQueries
from app.Core.config import settings

logger = logging.getLogger(__name__)


class DBManager(IDBManager[AddFileDbDTO, AddChannelDbDTO]):
    # -----init---------------------------------------------
    def __init__(self):
        self._db_path = settings.DB_PATH
        self._db_connection: Optional[aiosqlite.Connection] = None
    # -------------------------------------------------------

    # --------inheritance functions-------------------------
    async def start_connection(self) -> None:
        if not self._db_connection:
            try:
                self._db_connection = await aiosqlite.connect(self._db_path, timeout=30.0)
                self._db_connection.row_factory = aiosqlite.Row
                
                await self._db_connection.execute("PRAGMA busy_timeout = 30000;")
                await self._db_connection.execute("PRAGMA foreign_keys = ON;")
                await self._db_connection.execute("PRAGMA journal_mode = WAL;")
                
                await self._db_connection.executescript(InitScript.INIT_DB_SCRIPT)
                await self._db_connection.commit()
                logger.info("SQLite database connection established successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize SQLite database: {e}")
                raise e

    async def close_connection(self) -> None:
        if self._db_connection:
            await self._db_connection.close()
            self._db_connection = None
            logger.info("SQLite database connection closed gracefully.")
    # -------------------------------------------------------

    # ---------For files storage-----------------------------
    async def add_source_file(self, request: AddFileDbDTO) -> None:
        if not self._db_connection:
            raise RuntimeError("Database connection is not open.")

        file_type_val = (
            request.file_type.value
            if hasattr(request.file_type, "value")
            else str(request.file_type)
        )

        async with self._db_connection.execute(
            DbQueries.INSERT_SOURCE_FILE,
            (request.path, file_type_val, request.size),
        ):
            await self._db_connection.commit()
            logger.info(f"Source file added to database: {request.path}")

    async def remove_source_file(self, request: RemoveFileDbDTO) -> None:
        if not self._db_connection:
            raise RuntimeError("Database connection is not open.")

        async with self._db_connection.execute(DbQueries.DELETE_SOURCE_FILE, (request.path,)):
            await self._db_connection.commit()
            logger.info(f"Source file removed from database: {request.path}")
    # -------------------------------------------------------

    # ---------For streams connections----------------------
    async def add_channel(self, request: AddChannelDbDTO) -> None:
        if not self._db_connection:
            raise RuntimeError("Database connection is not open.")

        file_type_val = (
            request.file_type.value
            if hasattr(request.file_type, "value")
            else str(request.file_type)
        )

        async with self._db_connection.execute(
            DbQueries.INSERT_CHANNEL,
            (request.source_file_id, request.kafka_partition, file_type_val),
        ):
            await self._db_connection.commit()
            logger.info(
                f"Channel registered for source_file_id={request.source_file_id} on partition={request.kafka_partition}"
            )

    async def get_channels(self) -> List[Dict[str, Any]]:
        if not self._db_connection:
            raise RuntimeError("Database connection is not open.")

        async with self._db_connection.execute(DbQueries.GET_ALL_CHANNELS) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_source_file_id(self, path: str) -> Optional[int]:
        if not self._db_connection:
            raise RuntimeError("Database connection is not open.")

        async with self._db_connection.execute(
            DbQueries.GET_SOURCE_FILE_ID_BY_PATH,
            (path,)
        ) as cursor:
            answer = await cursor.fetchone()
            return answer["id"] if answer else None
    # -------------------------------------------------------