from abc import ABC, abstractmethod
from app.DTOs.KafkaDTOs import KafkaMessageDTO
class IKafkaProducerService(ABC):

    @abstractmethod
    async def start(self) -> None:
        pass

    @abstractmethod
    async def stop(self) -> None:
        pass

    @abstractmethod
    async def send_message(self, message: KafkaMessageDTO)-> None:
        pass