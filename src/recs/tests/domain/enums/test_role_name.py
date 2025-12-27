"""Тесты для перечисления ролей пользователя."""

import pytest

from lib.domain.enums.role_name import RoleName


@pytest.mark.parametrize(
    ("role", "expected_value"),
    [
        (RoleName.USER, "user"),
        (RoleName.ADMIN, "admin"),
        (RoleName.MODERATOR, "moderator"),
    ],
)
def test_role_name_value(role: RoleName, expected_value: str) -> None:
    """Тест значений ролей."""
    assert role == expected_value
    assert role.value == expected_value


@pytest.mark.parametrize(
    "role",
    [RoleName.USER, RoleName.ADMIN, RoleName.MODERATOR],
)
def test_role_name_enum_membership(role: RoleName) -> None:
    """Тест, что все роли являются членами перечисления."""
    assert role in RoleName


@pytest.mark.parametrize(
    ("role", "expected_string"),
    [
        (RoleName.USER, "user"),
        (RoleName.ADMIN, "admin"),
        (RoleName.MODERATOR, "moderator"),
    ],
)
def test_role_name_string_comparison(role: RoleName, expected_string: str) -> None:
    """Тест сравнения ролей со строками."""
    assert role == expected_string


def test_role_name_inequality():
    """Тест неравенства разных ролей."""
    assert RoleName.USER != RoleName.ADMIN
    assert RoleName.ADMIN != RoleName.MODERATOR
    assert RoleName.USER != RoleName.MODERATOR


def test_role_name_list_all_values():
    """Тест получения всех значений ролей."""
    expected_roles_count = 3
    all_roles = [role.value for role in RoleName]
    assert "user" in all_roles
    assert "admin" in all_roles
    assert "moderator" in all_roles
    assert len(all_roles) == expected_roles_count
