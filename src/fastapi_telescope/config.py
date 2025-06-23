from pydantic import Field
from pydantic_settings import BaseSettings

class DatabaseConfig(BaseSettings):
    user: str = Field(description='database user', alias='DB_USER')
    password: str = Field(description='database password', alias='DB_PASSWORD')
    host: str = Field(description='database host', alias='DB_HOST')
    port: int = Field(description='database port', alias='DB_PORT')
    name: str = Field(description='database name', alias='DB_NAME')

    @property
    def async_url(self) -> str:
        return f'postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}'


def get_db_config() -> DatabaseConfig:
    return DatabaseConfig() 


class APIConfig(BaseSettings):
    site_url: str = Field(description='site url', alias='SITE_URL')
    api_prefix: str = Field(description='api prefix', alias='API_PREFIX')

def get_api_config() -> APIConfig:
    return APIConfig()  # type: ignore