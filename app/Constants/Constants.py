class ProgramConstants:
    WRITE_BIN = "wb"
    READ_BIN = 'rb'
    WRITE = 'w'
    READ_CHUNK_SIZE = 1024 * 1024
    FILE_NOT_EXISTS = "file is not exists in the services"
    BYTE_ENCODEING = "utf-8"
    ENCODED_FILE_ENDING = '_decoded.txt'
    VALID_EXTENSION = '.bin'

class FastConf:
    #---------fastapi program------------
    TITLE = "Telemetry Simulator API""API for receiving and managing telemetry files"
    DESCRIPTION = "Telemetry Simulator API""API for receiving and managing telemetry files"
    VALID_EXTENSION = ".bin"
    APP_URL = "/api/{0}/ts"
    APP_TAG = "Telemetry Stream"

    STARTUP_COMPLETED = "Application startup completed successfully"
    STARTUP_FAILED = "Application startup failed"

    SHUTDOWN_STARTED = "Shutting down application..."
    SHUTDOWN_COMPLETED = "Application shutdown completed"

    KAFKA_PRODUCER_STOPPED = "Kafka producer stopped"
    KAFKA_PRODUCER_STOP_FAILED = "Failed to stop Kafka producer"

    DATABASE_CONNECTION_CLOSED = "Database connection closed"
    DATABASE_CONNECTION_CLOSE_FAILED = "Failed to close database connection"

    APP_MODULE = "app.main:app"

class KafkaConst:
    MAX_PARTITIONS = 10
    NEW_DRONE_PARAM ="server_drone_id"