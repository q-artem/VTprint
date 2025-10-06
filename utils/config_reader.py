from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    bot_token: SecretStr | None
    balakshin_pass: SecretStr | None
    vt_pass: SecretStr | None
    prodmat_pass: SecretStr | None
    elite_pass: SecretStr | None
    admin_pass: SecretStr | None
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

config = Settings() # type: ignore