from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class KafkaMessageDTO(BaseModel):
    topic: str = Field(..., description="Target Kafka topic name")
    value: Dict[str, Any] = Field(..., description="Payload containing the telemetry frame")
    key: Optional[str] = Field(None, description="Message key (e.g. PlatformTailNumber) for partition ordering")