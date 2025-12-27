"""Провайдеры для контейнера зависимостей."""

from collections.abc import AsyncIterable, AsyncIterator
import os

from dishka import (
    Provider,
    Scope,
    WithParents,
    provide,  # pyright: ignore[reportUnknownVariableType]
    provide_all,
)
import pydantic
from qdrant_client import AsyncQdrantClient
from sentence_transformers import SentenceTransformer
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from lib.application.gateways.qdrant_place_repository import IQdrantPlaceRepository
from lib.application.interactors.place_interactor import (
    CreatePlaceInteractor,
    DeletePlaceInteractor,
    GetPlaceInteractor,
    SearchPlacesInteractor,
    UpdatePlaceInteractor,
)
from lib.application.services.place_service import PlaceService
from lib.infra.db.uow import SQLAlchemyUnitOfWork
from lib.infra.repositories.place_repository import SQLAlchemyPlaceRepository
from lib.infra.repositories.qdrant_place_repository import QdrantPlaceRepository
from lib.infra.repositories.role_repository import SQLAlchemyRoleRepository
from lib.infra.repositories.ugc_repository import SQLAlchemyUGCRepository
from lib.infra.repositories.user_repository import SQLAlchemyUserRepository
from lib.main.settings import AppSettings, DatabaseSettings, QdrantSettings, Settings


class SettingsProvider(Provider):
    """Провайдер для настроек приложения."""

    @provide(scope=Scope.APP)
    async def get_settings(self) -> Settings:
        """
        Создает и возвращает настройки приложения.

        :return: Экземпляр настроек приложения
        """
        base_defaults = Settings()
        app_defaults = base_defaults.app
        db_defaults = base_defaults.db
        qdrant_defaults = base_defaults.qdrant

        def _bool_env(var: str, default: bool) -> bool:
            value = os.getenv(var)
            if value is None:
                return default
            return value.lower() in {"1", "true", "yes", "on"}

        db_password = os.getenv("DB_PASSWORD", db_defaults.password.get_secret_value())

        return Settings(
            app=AppSettings(
                env=os.getenv("APP_ENV", app_defaults.env),
                debug=_bool_env("APP_DEBUG", app_defaults.debug),
            ),
            db=DatabaseSettings(
                driver=os.getenv("DB_DRIVER", db_defaults.driver),
                name=os.getenv("DB_NAME", db_defaults.name),
                host=os.getenv("DB_HOST", db_defaults.host),
                port=int(os.getenv("DB_PORT", db_defaults.port)),
                user=os.getenv("DB_USER", db_defaults.user),
                password=pydantic.SecretStr(db_password),
                pool_size=int(os.getenv("DB_POOL_SIZE", db_defaults.pool_size)),
                pool_pre_ping=_bool_env("DB_POOL_PRE_PING", db_defaults.pool_pre_ping),
                echo=_bool_env("DB_ECHO", db_defaults.echo),
            ),
            qdrant=QdrantSettings(
                url=os.getenv("QDRANT_URL", qdrant_defaults.url),
                api_key=os.getenv("QDRANT_API_KEY", qdrant_defaults.api_key),
                collection_name=os.getenv("QDRANT_COLLECTION", qdrant_defaults.collection_name),
                vector_size=int(os.getenv("QDRANT_VECTOR_SIZE", qdrant_defaults.vector_size)),
            ),
        )

    @provide(scope=Scope.APP)
    async def get_database_settings(self, settings: Settings) -> DatabaseSettings:
        """
        Получает настройки базы данных из общих настроек.

        :param settings: Настройки приложения
        :return: Настройки базы данных
        """
        return settings.db

    @provide(scope=Scope.APP)
    async def get_qdrant_settings(self, settings: Settings) -> QdrantSettings:
        """
        Получает настройки Qdrant из общих настроек.

        :param settings: Настройки приложения
        :return: Настройки Qdrant
        """
        return settings.qdrant


class DatabaseProvider(Provider):
    """Провайдер БД."""

    scope = Scope.REQUEST

    @provide(scope=Scope.APP)
    async def engine(self, config: DatabaseSettings) -> AsyncIterator[AsyncEngine]:
        """
        Создание движка.

        :param config: Настройки базы данных
        :yield: Асинхронный движок SQLAlchemy
        """
        engine = create_async_engine(config.dsn)
        yield engine
        await engine.dispose()

    @provide(scope=Scope.APP)
    def get_sessionmaker(
        self,
        engine: AsyncEngine,
        config: DatabaseSettings,
    ) -> async_sessionmaker[AsyncSession]:
        """
        Создание sessionmaker.

        :param engine: Асинхронный движок SQLAlchemy
        :param config: Настройки базы данных
        :return: Фабрика сессий
        """
        return async_sessionmaker(
            engine,
            expire_on_commit=config.expire_on_commit,
            class_=AsyncSession,
            autoflush=config.auto_flush,
            autocommit=config.auto_commit,
        )

    @provide
    async def get_session(
        self,
        factory: async_sessionmaker[AsyncSession],
    ) -> AsyncIterable[AsyncSession]:
        """
        Создание сессии.

        :param factory: Фабрика сессий
        :yield: Асинхронная сессия SQLAlchemy
        """
        async with factory() as session:
            yield session


class QdrantProvider(Provider):
    """Провайдер Qdrant."""

    scope = Scope.REQUEST

    @provide(scope=Scope.APP)
    def get_qdrant_client(self, settings: QdrantSettings) -> AsyncQdrantClient:
        """
        Создает асинхронный клиент Qdrant.

        :param settings: Настройки Qdrant
        :return: Асинхронный клиент Qdrant
        """
        if settings.api_key:
            return AsyncQdrantClient(url=settings.url, api_key=settings.api_key)
        return AsyncQdrantClient(url=settings.url)

    @provide(scope=Scope.REQUEST)
    def get_qdrant_place_repository(
        self,
        client: AsyncQdrantClient,
        settings: QdrantSettings,
        postgres_place_repo: SQLAlchemyPlaceRepository,
    ) -> IQdrantPlaceRepository:
        """
        Создает репозиторий мест в Qdrant.

        :param client: Клиент Qdrant
        :param settings: Настройки Qdrant
        :param postgres_place_repo: Репозиторий PostgreSQL для получения полных данных
        :return: Репозиторий мест в Qdrant
        """
        return QdrantPlaceRepository(client, settings, postgres_place_repo)


class GatewayProvider(Provider):
    """Провайдер репозиториев."""

    scope = Scope.REQUEST

    repositories = provide_all(
        WithParents[SQLAlchemyRoleRepository],
        WithParents[SQLAlchemyUserRepository],
        WithParents[SQLAlchemyPlaceRepository],
        WithParents[SQLAlchemyUGCRepository],
    )


class ServiceProvider(Provider):
    """Провайдер сервисов."""

    scope = Scope.REQUEST

    @provide(scope=Scope.APP)
    def get_embedding_model(self) -> SentenceTransformer:
        """
        Создает модель для генерации эмбеддингов.

        :return: Модель SentenceTransformer
        """
        return SentenceTransformer("all-MiniLM-L6-v2")

    services = provide_all(
        WithParents[PlaceService],
    )


class InteractorProvider(Provider):
    """Провайдер интеракторов."""

    scope = Scope.REQUEST

    interactors = provide_all(
        WithParents[CreatePlaceInteractor],
        WithParents[GetPlaceInteractor],
        WithParents[UpdatePlaceInteractor],
        WithParents[DeletePlaceInteractor],
        WithParents[SearchPlacesInteractor],
    )


class InfrastructureProvider(Provider):
    """Провайдер инфраструктуры/адаптеров."""

    scope = Scope.REQUEST

    uow = provide_all(
        WithParents[SQLAlchemyUnitOfWork],
    )


__all__ = [
    "DatabaseProvider",
    "GatewayProvider",
    "InfrastructureProvider",
    "InteractorProvider",
    "QdrantProvider",
    "ServiceProvider",
    "SettingsProvider",
]
