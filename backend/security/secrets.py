"""Lecture centralisee des variables d'environnement (.env).

Principe 11 : aucun secret n'est stocke en dur dans le code ou le depot Git.
Toutes les valeurs sensibles transitent par ce module, lui-meme alimente par
un fichier .env local (non versionne).
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    secret_key: str = "changeme-generate-a-long-random-string"
    access_token_expire_minutes: int = 60

    database_url: str = "sqlite:///./ai_commerce_builder.db"

    admin_email: str = "admin@example.com"
    admin_password: str = "changeme"

    anthropic_api_key: str = ""

    payment_provider_active: str = "yas_tmoney,moov_money,card,manual"
    payment_simulate: bool = True

    cinetpay_api_key: str = ""
    cinetpay_site_id: str = ""
    cinetpay_enabled: bool = False

    @property
    def active_payment_providers(self) -> list[str]:
        return [p.strip() for p in self.payment_provider_active.split(",") if p.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
