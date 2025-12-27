"""
Утилиты и базовые инструменты для работы с настройками pydantic.

Предоставляет классы для загрузки и обработки конфигурации
из YAML-файлов с поддержкой подстановки переменных окружения.
"""

import logging
import os
import pathlib
import typing

import pydantic_settings

logger = logging.getLogger(__name__)


class EnvExpandedYamlConfigSettingsSource(pydantic_settings.YamlConfigSettingsSource):
    """
    Источник настроек из YAML-файла с поддержкой подстановки переменных окружения в строках.
    """

    T = typing.TypeVar("T")

    def _read_file(self, file_path: pathlib.Path) -> dict[str, typing.Any]:
        """
        Чтение и обработка YAML-файла с заменой переменных окружения в строках.

        :param file_path: Путь к YAML-файлу
        :return: Словарь с настройками, где значения строк с переменными окружения были подставлены
        """
        result = super()._read_file(file_path)
        return self._populate_dict(result)

    def _populate(self, data: T) -> T:
        """
        Рекурсивная подстановка переменных окружения в значения конфигурации.

        :param data: Значение произвольного типа (dict, list, str)
        :return: Значение с подставленными переменными окружения (если применимо)
        """
        if isinstance(data, dict):
            return self._populate_dict(data)  # pyright: ignore[reportUnknownArgumentType, reportUnknownVariableType]
        if isinstance(data, list):
            return self._populate_list(data)  # pyright: ignore[reportUnknownArgumentType, reportUnknownVariableType]
        if isinstance(data, str):
            return os.path.expandvars(data)
        return data

    def _populate_dict(self, data: dict[str, T]) -> dict[str, T]:
        """
        Подстановка переменных окружения в словаре настроек.

        :param data: Словарь с произвольными значениями
        :return: Обновленный словарь с подстановкой переменных окружения
        """
        return {key: self._populate(value) for key, value in data.items()}

    def _populate_list(self, data: list[T]) -> list[T]:
        """
        Подстановка переменных окружения в списке настроек.

        :param data: Список с произвольными значениями
        :return: Обновленный список с подстановкой переменных окружения
        """
        return [self._populate(value) for value in data]


class BaseSettings(pydantic_settings.BaseSettings):
    """
    Базовый класс настроек приложения с поддержкой вложенных переменных окружения и YAML-файлов.

    :var SETTINGS_PATH_ENV_NAME: Название переменной окружения с путем до YAML-файла настроек
    """

    SETTINGS_PATH_ENV_NAME: typing.ClassVar[str] = "SETTINGS_PATH"

    model_config = pydantic_settings.SettingsConfigDict(
        env_nested_delimiter="__",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[pydantic_settings.BaseSettings],
        init_settings: pydantic_settings.PydanticBaseSettingsSource,  # noqa: ARG003
        env_settings: pydantic_settings.PydanticBaseSettingsSource,
        dotenv_settings: pydantic_settings.PydanticBaseSettingsSource,  # noqa: ARG003
        file_secret_settings: pydantic_settings.PydanticBaseSettingsSource,  # noqa: ARG003
    ) -> tuple[pydantic_settings.PydanticBaseSettingsSource, ...]:
        """
        Переопределение порядка источников конфигурации.

        Сначала используются переменные окружения, затем YAML-файл,
        указанный в переменной окружения SETTINGS_PATH.

        :param settings_cls: Класс настроек, для которого настраиваются источники
        :param init_settings: Источник настроек из параметров инициализации
        :param env_settings: Источник настроек из переменных окружения
        :param dotenv_settings: Источник настроек из .env файлов
        :param file_secret_settings: Источник настроек из секретов
        :return: Кортеж с источниками настроек в приоритетном порядке
        """
        return (
            env_settings,
            *cls.get_settings_yaml_sources(
                settings_cls,
                cls.SETTINGS_PATH_ENV_NAME,
            ),
        )

    @classmethod
    def get_settings_yaml_sources(
        cls,
        settings_cls: type[pydantic_settings.BaseSettings],
        settings_yaml_env_name: str,
    ) -> typing.Sequence[pydantic_settings.YamlConfigSettingsSource]:
        """
        Получение настроек из YAML файлов, указанных в переменной окружения.

        :param settings_cls: Базовый класс настроек (для model_config)
        :param settings_yaml_env_name: Название переменной окружения с файлами настроек
        :return: Список источников настроек из YAML-файлов
        """
        setting_yaml_env = os.environ.get(settings_yaml_env_name, None)

        if setting_yaml_env is None:
            return []

        paths = setting_yaml_env.split(":")

        for path in paths:
            if not pathlib.Path(path).exists():
                msg = f"Файл с настройками не найден: {path}"
                raise FileNotFoundError(msg)

        return [
            EnvExpandedYamlConfigSettingsSource(
                settings_cls,
                yaml_file=path,
            )
            for path in paths
        ]
