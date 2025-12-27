"""Конфигурация логирования для приложения."""

import dataclasses
import logging
import logging.config as logging_config
import sys
import typing

LogLevel = typing.Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def initialize_logging(
    config: dict[str, typing.Any],
) -> None:
    """
    Инициализация логирования с заданной конфигурацией.

    :param config: Словарь с конфигурацией логирования
    """

    logging_config.dictConfig(config)


@dataclasses.dataclass
class LoggerConfig:
    """
    Конфигурация для отдельного логгера.

    :param propagate: Распространять ли сообщения в родительские логгеры
    :param level: Уровень логирования
    """

    propagate: bool
    level: LogLevel | None = None


def create_config(
    log_level: LogLevel,
    log_format: str,
    loggers: dict[str, LoggerConfig] | None = None,
) -> dict[str, typing.Any]:
    """
    Создает конфигурацию логирования.

    :param log_level: Уровень логирования по умолчанию
    :param log_format: Формат сообщений
    :param loggers: Словарь с конфигурацией для отдельных логгеров
    :return: Словарь с конфигурацией логирования
    """

    config: dict[str, typing.Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "default": {
                "stream": sys.stdout,
                "level": log_level,
                "formatter": "default",
                "class": "logging.StreamHandler",
            },
        },
        "formatters": {
            "default": {
                "()": lambda: logging.Formatter(fmt=log_format),
            },
        },
        "root": {
            "level": log_level,
            "handlers": ["default"],
        },
    }

    if loggers:
        config["loggers"] = {
            logger_name: {
                "handlers": ["default"],
                "level": logger_config.level or log_level,
                "propagate": logger_config.propagate,
            }
            for logger_name, logger_config in loggers.items()
        }

    return config


__all__ = [
    "LogLevel",
    "LoggerConfig",
    "create_config",
    "initialize_logging",
]
