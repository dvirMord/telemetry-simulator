# ------------Recive file ROs massges------------------------------
class FilesControllerROsMessages:

    class Success:
        FILE_RECEIVE_AND_SAVE = "File: {0} , received and saved successfully."
        DELETE_SUCCESS_TEMPLATE = 'File: "{0}" Deleted successfully.'

    class Error:
        EXTENTSION_NOT_VALID = "Extenstion is not valid, only bin files!"
        FILE_SAVE_FAILED_TEMPLATE = "Failed to save file: {0} error: {1}"
        FILE_RECEIVE_FAILED_TEMPLATE = "Failed to receive file: {0}"
        FILE_DELETE_FAILED_TEMPLATE = "Failed to delete file: {0} error: {1}"
        FILE_NOT_FOUND_BY_ID = "Source file with SimId '{0}' was not found in database."
# --------------------------------------------------------------------


class FilesLogMessages:
    DELETE_FILES_ERROR = "Failed to delete files for SimId %s: %s"


class FileExtensions:
    RAW_BIN_EXTENSION = ".bin"