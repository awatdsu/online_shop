from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr  

class EmailSettings(BaseSettings):  
    email_host: str  
    email_port: int  
    email_username: str  
    email_password: SecretStr  

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf8", extra="ignore")  


class RedisSettings(BaseSettings):  
    redis_host: str  
    redis_port: int  
    redis_db: int  

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf8", extra="ignore")  

    @property  
    def redis_url(self):  
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

class DbSettings(BaseSettings):
    db_user: str
    db_password: SecretStr
    db_host: str
    db_port: int
    db_name: str


    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf8", extra="ignore")

    @property
    def postgres_url(self):
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password.get_secret_value()}@{self.db_host}:{self.db_port}/{self.db_name}"

class JwtSettings(BaseSettings):
    secret_key: SecretStr
    algorithm: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf8", extra="ignore")

class CsrfSettings(BaseSettings):
    secret_key_csrf: SecretStr
    salt_csrf: SecretStr

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf8", extra="ignore")

class UrlSecretKeys(BaseSettings):
    secret_key_url_reg: SecretStr
    secret_key_url_pwd: SecretStr

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf8", extra="ignore")

class Settings(BaseSettings):   
    email_settings: EmailSettings = EmailSettings()  
    redis_settings: RedisSettings = RedisSettings()
    postgres_settings: DbSettings = DbSettings()
    jwt_settings: JwtSettings = JwtSettings()
    csrf_settings: CsrfSettings = CsrfSettings()
    url_secret_keys: UrlSecretKeys = UrlSecretKeys()

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf8", extra="ignore")  


settings = Settings()


__all__ = ("settings",)
