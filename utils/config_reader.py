from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    bot_token: SecretStr
    balakshin_pass: SecretStr
    vt_pass: SecretStr
    prodmat_pass: SecretStr
    elite_pass: SecretStr
    admin_pass: SecretStr
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

config = Settings()