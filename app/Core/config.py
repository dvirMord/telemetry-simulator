from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    #--------app settings--------
    PORT: int 
    IP: str 
    CURRENT_VERSION: str
    #----------------------------

    #--------. env---------------
    SERVICE_NAME: str
    STORAGE_PATH: str
    STORAGE_DECODED_PATH: str
    #----------------------------

    #--------kafka config--------
    KAFKA_BROKER_URL: str
    MAIN_TOPIC_NAME:str
    DEFAULT_PARTITIONS_NUMBER:int


    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()