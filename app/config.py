import re
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    base_url: str = "https://v2.samehadaku.how"
    port: int = 3000
    api_prefix: str = "/api/v1"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()


def build_url(path: str) -> str:
    return f"{settings.base_url}{path}"


_SLUG_DOMAIN_PATTERN = re.compile(r"^https?://[^/]+/")


def extract_slug(url: str, prefix: str) -> str:
    pattern = re.compile(rf"^https?://[^/]+/{prefix}/")
    return pattern.sub("", url).rstrip("/")