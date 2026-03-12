from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db_name: str = "metadata_inventory"
    http_timeout: int = 10
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    class Config: 
        model_config = {"env_file": ".env"}

settings = Settings()
