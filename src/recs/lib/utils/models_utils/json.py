"""
Утилиты для работы с JSON.

Предоставляет типы и функции для сериализации и десериализации
данных в формате JSON.
"""

import typing

import orjson

# Определение типов для сериализуемых объектов JSON
JsonSerializableType = str | int | float | bool | None
JsonSerializable = JsonSerializableType | typing.Mapping[str, "JsonSerializable"] | typing.Sequence["JsonSerializable"]
JsonSerializableDict = typing.Mapping[str, JsonSerializable]
JsonSerializableList = typing.Sequence[JsonSerializable]

# Функции для работы с JSON
dumps_bytes = orjson.dumps
loads_bytes = orjson.loads


def dumps_str(obj: JsonSerializable) -> str:
    """
    Сериализует объект Python в JSON-строку.

    :param obj: Объект, который нужно сериализовать в строку
    :return: Строка в формате JSON, представляющая объект
    """

    return dumps_bytes(obj).decode("utf-8")


def loads_str(s: str) -> JsonSerializable:
    """
    Десериализация строки в объект Python из формата JSON.

    :param s: Строка в формате JSON
    :return: Объект Python, соответствующий данным из JSON-строки
    """

    return loads_bytes(s.encode("utf-8"))


__all__ = [
    "JsonSerializable",
    "JsonSerializableDict",
    "JsonSerializableList",
    "JsonSerializableType",
    "dumps_bytes",
    "dumps_str",
    "loads_bytes",
    "loads_str",
]
