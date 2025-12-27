"""
Утилиты для работы со схемами данных.

Предоставляет базовые классы и функции для сериализации
и десериализации данных
"""

import enum
import typing

import msgpack
import pydantic

import lib.utils.models_utils.json as json_utils


def resolve_enum_value(data: typing.Any) -> typing.Any:  # noqa: ANN401
    """
    Функция для получения значения из Enum или возврата данных без изменений.

    :param data: Данные произвольного типа
    :return: Значение из Enum, если data является экземпляром Enum, иначе возвращается data
    """

    if isinstance(data, enum.Enum):
        return data.value

    return data


class BaseSchema(pydantic.BaseModel):
    """
    Базовая модель для сериализации данных.

    Расширяет Pydantic BaseModel, добавляя методы для работы
    с форматами MessagePack и JSON. Поддерживает сериализацию
    как в байтовом представлении, так и в строковом формате.
    """

    @classmethod
    def from_bytes(cls, data: bytes) -> typing.Self:
        """
        Создает объект модели из данных в формате MessagePack.

        :param data: Байтовая строка в формате MessagePack
        :return: Экземпляр модели с данными из MessagePack
        """
        raw_data = msgpack.loads(data)  # pyright: ignore[reportUnknownVariableType]
        return cls.model_validate(raw_data)

    def to_bytes(self) -> bytes:
        """
        Сериализует модель в формат MessagePack.

        :return: Байтовая строка в формате MessagePack
        """
        raw_data = self.model_dump()
        return msgpack.dumps(  # pyright: ignore[reportUnknownVariableType, reportReturnType]
            raw_data,
            default=resolve_enum_value,
        )

    @classmethod
    def from_json_bytes(cls, data: bytes) -> typing.Self:
        """
        Создает объект модели из JSON в байтовом представлении.

        :param data: JSON-данные в байтовом представлении
        :return: Экземпляр модели с данными из JSON
        """
        raw_data = json_utils.loads_bytes(data)
        return cls.model_validate(raw_data)

    def to_json_bytes(self) -> bytes:
        """
        Сериализует модель в JSON в байтовом представлении.

        :return: JSON-данные в байтовом представлении
        """
        raw_data = self.model_dump()
        return json_utils.dumps_bytes(raw_data)

    @classmethod
    def from_json_str(cls, data: str) -> typing.Self:
        """
        Создает объект модели из JSON-строки.

        :param data: JSON-строка
        :return: Экземпляр модели с данными из JSON
        """
        raw_data = json_utils.loads_str(data)
        return cls.model_validate(raw_data)

    def to_json_str(self) -> str:
        """
        Сериализует модель в JSON-строку.

        :return: Строка в формате JSON
        """
        raw_data = self.model_dump()
        return json_utils.dumps_str(raw_data)


__all__ = [
    "BaseSchema",
]
