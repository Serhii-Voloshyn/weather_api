from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    aws_access_key: str
    aws_secret_key: str
    weather_api_key: str
    aws_region_name: str
    s3_bucket_name: str
    dynamodb_table_name: str
    cache_expiry_minutes: int

    class Config:
        env_file = ".env"

settings = Settings()