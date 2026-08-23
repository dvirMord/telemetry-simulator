import json
import logging
from typing import Optional
from aiokafka import AIOKafkaProducer
from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from app.Interfaces.IKafkaProducerService import IKafkaProducerService
from app.DTOs.KafkaDTOs import KafkaMessageDTO
from app.Core.config import settings
from app.Constants.Constants import ProgramConstants
from app.Constants.KafkaMessages import KafkaMessages

# Configure stream handler to ensure console output
logger = logging.getLogger(__name__)
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)


class KafkaProducerService(IKafkaProducerService):

    def __init__(self, bootstrap_servers: Optional[str] = None):
        self._bootstrap_servers = bootstrap_servers or settings.KAFKA_BROKER_URL
        self._producer: Optional[AIOKafkaProducer] = None

    async def _ensure_topic_exists(self, topic_name: str, num_partitions: int = 10) -> None:
        """Create the topic with desired partitions if it does not exist."""
        admin_client = AIOKafkaAdminClient(bootstrap_servers=self._bootstrap_servers)
        try:
            await admin_client.start()
            existing_topics = await admin_client.list_topics()
            if topic_name not in existing_topics:
                topic = NewTopic(name=topic_name, num_partitions=num_partitions, replication_factor=1)
                await admin_client.create_topics([topic])
                logger.info(KafkaMessages.TOPIC_CREATED_SUCCESS.format(topic_name, num_partitions))
        except Exception as e:
            logger.warning(f"Topic auto-check skipped: {e}")
        finally:
            await admin_client.close()

    async def start(self) -> None:
        """Initialize the Kafka producer, check partitions, and establish broker connection."""
        try:
            # Ensure the main topic exists with 10 partitions
            topic_name = getattr(settings, "MAIN_TOPIC_NAME", "telemetry.frames.raw")
            await self._ensure_topic_exists(topic_name, num_partitions=10)

            self._producer = AIOKafkaProducer(
                bootstrap_servers=self._bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode(ProgramConstants.BYTE_ENCODEING),
                key_serializer=lambda k: k.encode(ProgramConstants.BYTE_ENCODEING) if k else None,
            )
            await self._producer.start()

            partitions = await self._producer.partitions_for(topic_name)
            logger.info(KafkaMessages.TOPIC_PARTITIONS_INFO.format(topic_name, partitions))
            logger.info(KafkaMessages.PRODUCER_START_SUCCESS.format(self._bootstrap_servers))
        except Exception as e:
            logger.error(KafkaMessages.PRODUCER_START_FAILED.format(str(e)))
            raise e

    async def stop(self) -> None:
        """Close the Kafka producer connection gracefully."""
        if self._producer:
            await self._producer.stop()
            logger.info(KafkaMessages.PRODUCER_STOPPED_SUCCESS)

    async def send_message(self, message: KafkaMessageDTO) -> None:
        """Publish a message from the provided DTO payload."""
        if not self._producer:
            raise RuntimeError(KafkaMessages.PRODUCER_NOT_STARTED)

        try:
            await self._producer.send_and_wait(
                topic=message.topic, value=message.value, key=message.key, partition=message.partition)
        except Exception as e:
            logger.error(
                KafkaMessages.MESSAGE_SEND_ERROR.format(
                    message.topic, str(e)
                )
            )
            raise e