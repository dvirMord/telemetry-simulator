# app/services/telemetry_files_service.py
import asyncio
import os

import aiofiles
import aiofiles.os
import logging
from fastapi import UploadFile

from app.Constants.Constants import ProgramConstants
from app.Constants.ReciveFileMessages import *
from app.Core.config import settings
from app.DTOs.DBDTOs import AddFileDbDTO, FileType, RemoveFileDbDTO
from app.Interfaces.IDBManager import IDBManager
from app.Interfaces.IDecoderService import IMisbDecoder
from app.Interfaces.Itelemetry_files_service import ITelemetryFilesService
from app.ROSs.ReciveFileRos import *

logger = logging.getLogger(__name__)

class TelemetryFilesService(ITelemetryFilesService):
    def __init__(self, decoder: IMisbDecoder, dbManager: IDBManager):
        self.decoder = decoder
        self._db_service = dbManager

    #----------files - Recive and save file----------------------------------------------------
    async def Recive_file(self, file: UploadFile) -> FileSuccessResponse | FileErrorResponse:
        if not self.is_extentsion_valid(file.filename):
            uploadFIlePath  = FilesControllerROsMessages.Error.EXTENTSION_NOT_VALID
            return FileErrorResponse(message=FilesControllerROsMessages.Error.FILE_SAVE_FAILED_TEMPLATE.format(file.filename, uploadFIlePath ))
        
        uploadFile = settings.STORAGE_PATH

        os.makedirs(uploadFile, exist_ok=True)
        file_path = os.path.join(uploadFile, file.filename)

        try:
            async with aiofiles.open(file_path, ProgramConstants.WRITE_BIN) as dst_file:
                while content := await file.read(ProgramConstants.READ_CHUNK_SIZE): 
                    await dst_file.write(content)
                #------decoding the bin file-----------------------------
                decode_path, decoded_size = await asyncio.to_thread(self.decoder.decode, file_path)
                #--------------------------------------------------------

                #----------db objs-------------------------------
                bin_bd_obj: AddFileDbDTO = AddFileDbDTO(path=file_path, size=file.size, file_type=FileType.BIN)
                decode_db_obj: AddFileDbDTO = AddFileDbDTO(path=decode_path, size=decoded_size, file_type=FileType.DECODED)
                source_id_bin = await self._db_service.add_source_file(bin_bd_obj)
                source_id_decoded = await self._db_service.add_source_file(decode_db_obj)
            return FileSuccessUploadResponse(message=FilesControllerROsMessages.Success.FILE_RECEIVE_AND_SAVE.format(file.filename), decodedId=source_id_decoded)
        
        except Exception as e:   
            return FileErrorResponse(message=FilesControllerROsMessages.Error.FILE_SAVE_FAILED_TEMPLATE.format(file.filename, e))

        finally:
            await file.close()
            
    #---------------------------end---------------------------------------------------
     
    #interface----------------delete file from the service------------------------------------------- 
    async def Delete_file(self, sim_id: int) -> FileSuccessResponse | FileErrorResponse:
        decoded_file_name = await self._db_service.get_source_file_path_by_id(sim_id)
        if not decoded_file_name:
            return FileErrorResponse(
                message=FilesControllerROsMessages.Error.FILE_NOT_FOUND_BY_ID.format(sim_id)
            )

        decoded_path = os.path.join(settings.STORAGE_DECODED_PATH, decoded_file_name)

        base_name = decoded_file_name.replace(ProgramConstants.ENCODED_FILE_ENDING, "")
        raw_file_name = f"{base_name}{FileExtensions.RAW_BIN_EXTENSION}"
        raw_path = os.path.join(settings.STORAGE_PATH, raw_file_name)

        try:
            if os.path.exists(decoded_path):
                await aiofiles.os.remove(decoded_path)

            if os.path.exists(raw_path):
                await aiofiles.os.remove(raw_path)

            await self._db_service.remove_source_file(RemoveFileDbDTO(path=decoded_path))
            await self._db_service.remove_source_file(RemoveFileDbDTO(path=raw_path))

            return FileSuccessResponse(
                message=FilesControllerROsMessages.Success.DELETE_SUCCESS_TEMPLATE.format(decoded_file_name)
            )

        except Exception as e:
            logger.error(FilesLogMessages.DELETE_FILES_ERROR, sim_id, e)
            return FileErrorResponse(
                message=FilesControllerROsMessages.Error.FILE_DELETE_FAILED_TEMPLATE.format(decoded_file_name, str(e))
            )
    #----------------end--------------------------------------------------------------------

    def is_extentsion_valid(self, input: str) -> bool:
        return os.path.splitext(input)[1].lower() == ProgramConstants.VALID_EXTENSION