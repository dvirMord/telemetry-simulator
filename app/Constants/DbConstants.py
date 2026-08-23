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
    # Source Files Queries
    INSERT_SOURCE_FILE = """
        INSERT INTO source_files (path, type, size)
        VALUES (?, ?, ?)
    """

    DELETE_SOURCE_FILE = """
        DELETE FROM source_files
        WHERE path = ?;
    """

    GET_SOURCE_FILE_ID_BY_PATH = "SELECT id FROM source_files where path = ?"

    # Channels Queries
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