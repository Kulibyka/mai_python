"""Настройки проекта"""

import logging
import warnings

import pydantic

import lib.utils.logging as logging_utils

logger_ = logging.getLogger(__name__)


class AppSettings(pydantic.BaseModel):
    """Настройки приложения"""

    env: str = "production"
    debug: bool = False

    @property
    def is_development(self) -> bool:
        """Проверка, является ли приложение в режиме разработки"""
        return self.env == "development"

    @property
    def is_debug(self) -> bool:
        """Проверка, является ли приложение в режиме отладки"""
        if not self.is_development and self.debug:
            warnings.warn("APP_DEBUG is True не в режиме разработки!", UserWarning, stacklevel=2)

        return self.debug


class LoggingSettings(pydantic.BaseModel):
    """Настройки логирования"""

    level: logging_utils.LogLevel = "INFO"
    format: str = "%(asctime)s | %(levelname)-8s | %(module)s:%(lineno)d | %(message)s"
    loggers: dict[str, logging_utils.LoggerConfig] | None = None


class DatabaseSettings(pydantic.BaseModel):
    """Настройки для подключения к базе данных, определение настроек сессии"""

    # Connection settings
    driver: str = "postgresql+asyncpg"
    name: str = "nomad"
    host: str = "localhost"
    port: int = 5432
    user: str = "nomad"
    password: pydantic.SecretStr = pydantic.Field(default=pydantic.SecretStr("nomadpass"))

    # Engine settings
    pool_size: int = 50
    pool_pre_ping: bool = True
    echo: bool = False

    # Session settings
    auto_commit: bool = False
    auto_flush: bool = False
    expire_on_commit: bool = False

    @property
    def dsn(self) -> str:  # pragma: no cover
        """
        Генерация DSN строки подключения с паролем

        :return: DSN строка с паролем для подключения к базе данных
        """

        password = self.password.get_secret_value()
        return f"{self.driver}://{self.user}:{password}@{self.host}:{self.port}/{self.name}"

    @property
    def dsn_as_safe_url(self) -> str:
        """
        Генерация безопасного DSN без отображения пароля

        :return: DSN строка без пароля (заменён на `***`)
        """

        return f"{self.driver}://{self.user}:***@{self.host}:{self.port}"


class QdrantSettings(pydantic.BaseModel):
    """Настройки для подключения к Qdrant."""

    url: str = "http://localhost:6333"
    api_key: str | None = None
    collection_name: str = "places"
    vector_size: int = 384  # Размерность для модели all-MiniLM-L6-v2


class Settings(pydantic.BaseModel):
    """Настройки проекта"""

    app: AppSettings = pydantic.Field(default_factory=AppSettings)
    log: LoggingSettings = pydantic.Field(default_factory=LoggingSettings)
    db: DatabaseSettings = pydantic.Field(default_factory=DatabaseSettings)
    qdrant: QdrantSettings = pydantic.Field(default_factory=QdrantSettings)
