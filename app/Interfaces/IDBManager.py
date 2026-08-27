from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, TypeVar  # noqa: UP035

T_File = TypeVar("T_File")
T_Channel = TypeVar("T_Channel")


class IDBManager(ABC, Generic[T_File, T_Channel]):
    #----------init db--------------------------------------
    @abstractmethod
    async def start_connection(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def close_connection(self) -> None:
        raise NotImplementedError
    #-------------------------------------------------------

    #---------For files storage-----------------------------
    @abstractmethod
    async def add_source_file(self, request: T_File) -> None:
        raise NotImplementedError

    @abstractmethod
    async def remove_source_file(self, request: T_File) -> None:
        raise NotImplementedError
    #-------------------------------------------------------

    #---------For streams connctions------------------------
    @abstractmethod
    async def add_channel(self, request: T_Channel) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_channels(self) -> List[Dict[str, Any]]:
        raise NotImplementedError
    #-------------------------------------------------------
    @abstractmethod
    async def get_source_file_id(self, path: str):
        raise NotImplementedError