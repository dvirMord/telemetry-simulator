class StreamMessages:
    FILE_NOT_FOUND = "File '{0}' was not found on server."
    STREAM_STARTED = "Started streaming file '{0}' to Kafka topic '{1}'."
    STREAM_COMPLETED = "Completed streaming file '{0}'."
    STREAM_STOPPED = "Streaming for file '{0}' was stopped."
    STREAM_ALREADY_RUNNING = "Stream for file '{0}' is already running."
    STREAM_NOT_FOUND = "No active stream found for file '{0}'."
    INTERNAL_ERROR = "An internal error occurred: {0}"