class InitScript:
    INIT_DB_SCRIPT = """
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS source_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT NOT NULL UNIQUE,
        type TEXT NOT NULL,
        size INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS channels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_file_id INTEGER NOT NULL,
        kafka_partition INTEGER NOT NULL,
        type TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
        FOREIGN KEY (source_file_id) REFERENCES source_files(id) ON DELETE CASCADE
    );
    """


class DbQueries:
    # ------------------ source_files ------------------
    GET_SOURCE_FILE_PATH_BY_ID = """
        SELECT path 
        FROM source_files 
        WHERE id = ?;
    """

    INSERT_SOURCE_FILE = """
        INSERT INTO source_files (path, type, size)
        VALUES (?, ?, ?);
    """

    DELETE_SOURCE_FILE = """
        DELETE FROM source_files
        WHERE path = ?;
    """

    GET_SOURCE_FILE_ID_BY_PATH = """
        SELECT id 
        FROM source_files 
        WHERE path = ?;
    """

    # ------------------ channels ------------------
    INSERT_CHANNEL = """
        INSERT INTO channels (source_file_id, kafka_partition, type)
        VALUES (?, ?, ?);
    """

    GET_ALL_CHANNELS = """
        SELECT 
            c.id AS channel_id,
            c.kafka_partition,
            c.type,
            c.created_at,
            s.id AS source_file_id,
            s.path AS source_file_path,
            s.size AS source_file_size
        FROM channels c
        JOIN source_files s ON c.source_file_id = s.id
        ORDER BY c.created_at DESC;
    """


class DbLogMessages:
    # Errors & Exceptions
    DB_NOT_OPEN = "Database connection is not open."
    INIT_FAILED = "Failed to initialize SQLite database: {0}"

    # Connection Lifecycle
    CONNECTION_ESTABLISHED = "SQLite database connection established successfully."
    CONNECTION_CLOSED = "SQLite database connection closed gracefully."

    # Source Files
    SOURCE_FILE_ADDED = "Source file added to database: {0}"
    SOURCE_FILE_REMOVED = "Source file removed from database: {0}"

    # Channels
    CHANNEL_REGISTERED = "Channel registered for source_file_id={0} on partition={1}"

class Constants:
    path = "path"