# app/services/telemetry_files_service.py
import os
import aiofiles
import aiofiles.os 
from fastapi import UploadFile
from app.Interfaces.Itelemetry_files_service import ITelemetryFilesService
from app.Core.config import settings
from app.ROSs.ReciveFileRos import *
from app.Constants.ReciveFileMessages import *  
from app.Constants.Constants import ProgramConstants
from app.Interfaces.IDecoderService import IMisbDecoder
from app.Interfaces.IDBManager import IDBManager
from app.DTOs.DBDTOs import AddFileDbDTO, AddChannelDbDTO, RemoveFileDbDTO
from app.DTOs.DBDTOs import FileType
import asyncio

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
                await self._db_service.add_source_file(bin_bd_obj)
                await self._db_service.add_source_file(decode_db_obj)
            return FileSuccessResponse(message=FilesControllerROsMessages.Success.FILE_RECEIVE_AND_SAVE.format(file.filename))
        
        except Exception as e:
            return FileErrorResponse(message=FilesControllerROsMessages.Error.FILE_SAVE_FAILED_TEMPLATE.format(file.filename, e))

        finally:
            await file.close()
            
    #---------------------------end---------------------------------------------------
     
    #interface----------------delete file from the service------------------------------------------- 
    async def Delete_file(self, file_name: str) -> FileSuccessResponse | FileErrorResponse:
        if not self.is_extentsion_valid(file_name):
            msg = FilesControllerROsMessages.Error.EXTENTSION_NOT_VALID
            return FileErrorResponse(message=FilesControllerROsMessages.Error.FILE_SAVE_FAILED_TEMPLATE.format(file_name, msg))
        
        upload_dir = settings.STORAGE_PATH
        file_path = os.path.join(upload_dir, file_name)
        try:
            if not os.path.exists(file_path):
                return FileErrorResponse(
                    message=FilesControllerROsMessages.Error.FILE_DELETE_FAILED_TEMPLATE.format(
                        file_name, ProgramConstants.FILE_NOT_EXISTS))
            
            await aiofiles.os.remove(file_path)
            #---- decoded file name-----------------------------------------------------
            decoded_name = file_name.split('.')[0] + ProgramConstants.ENCODED_FILE_ENDING
            decoded_path = os.path.join(settings.STORAGE_DECODED_PATH, decoded_name) 
            #--------------end----------------------------------------------------------

            #---------delete from db------------------------------------------
            bin_file_db_dto: RemoveFileDbDTO = RemoveFileDbDTO(path=file_path)
            decoded_file_db_dto: RemoveFileDbDTO = RemoveFileDbDTO(path=decoded_path)
            await self._db_service.remove_source_file(bin_file_db_dto)
            await self._db_service.remove_source_file(decoded_file_db_dto)
            #-------------end-------------------------------------------------
            return FileSuccessResponse(
                message=FilesControllerROsMessages.Success.DELETE_SUCCESS_TEMPLATE.format(file_name)
            ) 
        except Exception as e:
            return FileErrorResponse(
                message=FilesControllerROsMessages.Error.FILE_DELETE_FAILED_TEMPLATE.format(file_name, e)
            )

    #----------------end--------------------------------------------------------------------

    def is_extentsion_valid(self, input: str) -> bool:
        return os.path.splitext(input)[1].lower() == ProgramConstants.VALID_EXTENSION