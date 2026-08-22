# app/dependencies.py
from fastapi import Depends

# ----------------------------interfaces----------------------------------------------
from app.Interfaces.Itelemetry_files_service import ITelemetryFilesService
from app.Interfaces.IDecoderService import IMisbDecoder
from app.Interfaces.IKafkaProducerService import IKafkaProducerService
from app.Interfaces.IStreamFilesService import IStreamFilesService
# -------------------------------end--------------------------------------------------

# -------------------------------services---------------------------------------------
from app.Services.TelemetrySimulatorServices.KlvFilesService.Telemetry_file_service import TelemetryFilesService
from app.Services.KlvDecoderService.DecoderService import MisbDecoder
from app.Services.KafkaService.KafkaProducerService import KafkaProducerService
from app.Services.TelemetrySimulatorServices.StreamsService.StreamFilesService import StreamFilesService
# ---------------------------------end------------------------------------------------

# -----------------------------singletons---------------------------------------------
_misb_decoder_instance: IMisbDecoder = MisbDecoder()
_kafka_producer_instance: IKafkaProducerService | None = None
_stream_files_service_instance: IStreamFilesService | None = None
_telemetry_files_service_instance: ITelemetryFilesService | None = None
# ---------------------------------end------------------------------------------------


def get_kafka_producer() -> IKafkaProducerService:
    """Return the global Kafka producer instance."""
    global _kafka_producer_instance
    if _kafka_producer_instance is None:
        _kafka_producer_instance = KafkaProducerService()
    return _kafka_producer_instance


def get_stream_files_service(
    kafka_producer: IKafkaProducerService = Depends(get_kafka_producer),
) -> IStreamFilesService:
    """Return the StreamFilesService instance."""
    global _stream_files_service_instance
    if _stream_files_service_instance is None:
        _stream_files_service_instance = StreamFilesService(kafka_producer)
    return _stream_files_service_instance


def get_misb_decoder() -> IMisbDecoder:
    """Return the global MISB decoder instance."""
    return _misb_decoder_instance


def get_telemetry_files_service(
    decoder: IMisbDecoder = Depends(get_misb_decoder),
) -> ITelemetryFilesService:
    """Return the global TelemetryFilesService instance."""
    global _telemetry_files_service_instance
    if _telemetry_files_service_instance is None:
        _telemetry_files_service_instance = TelemetryFilesService(decoder)
    return _telemetry_files_service_instance