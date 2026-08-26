class KafkaMessages:
    PRODUCER_START_SUCCESS = "KafkaProducerService successfully connected to {0}"
    PRODUCER_START_FAILED = "Failed to start Kafka Producer: {0}"
    PRODUCER_STOPPED_SUCCESS = "KafkaProducerService stopped successfully"
    PRODUCER_NOT_STARTED = "Kafka Producer is not started. Call start() first."
    MESSAGE_SEND_ERROR = "Error sending message to topic {0}: {1}"