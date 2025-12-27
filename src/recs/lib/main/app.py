"""Инициализация FastAPI приложения."""

from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager

from dishka import AsyncContainer  # noqa: TC002
from fastapi import FastAPI, Request, Response

from lib.main.ioc.di import create_app_context
from lib.present.api.v1 import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения.

    :param app: FastAPI приложение
    :yield: None
    """
    async with create_app_context() as container:
        app.state.container = container
        yield
        await container.close()


def create_app() -> FastAPI:
    """
    Создает и настраивает FastAPI приложение.

    :return: Настроенное FastAPI приложение
    """
    app = FastAPI(
        title="Echo Nomad API",
        description="API для поиска мест",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.include_router(api_router)

    @app.middleware("http")
    async def dishka_middleware(  # pyright: ignore[reportUnusedFunction]
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """
        Middleware для создания request-scoped контейнера.

        :param request: FastAPI request
        :param call_next: Следующий обработчик
        :return: Response
        """
        app_container: AsyncContainer = app.state.container
        async with app_container() as request_container:
            request.state.container = request_container
            return await call_next(request)

    return app


__all__ = [
    "create_app",
]
