from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

CATEGORIES = [
    "Рестораны",
    "Бары",
    "Кофейни",
    "Парки",
    "Музеи",
    "Активный отдых",
    "Кино",
    "Театры",
    "Шопинг",
    "Ночные клубы",
    "Любая",
]

PRICE_LEVELS = ["Любой", "Бюджетный", "Средний", "Премиум"]

MIN_RATINGS = [
    ("Любой", None),
    ("4.0+", 4.0),
    ("4.5+", 4.5),
]

MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎯 Найти место"), KeyboardButton(text="➕ Добавить место")],
        [KeyboardButton(text="💬 Профиль"), KeyboardButton(text="🏆 Топы")],
        [KeyboardButton(text="⚙️ Настройки и помощь")],
    ],
    resize_keyboard=True,
)


def find_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎭 По категории", callback_data="find:category")],
            [InlineKeyboardButton(text="🎲 Случайная рекомендация", callback_data="find:random")],
            [InlineKeyboardButton(text="🔍 Поиск по тексту", callback_data="find:search")],
            [InlineKeyboardButton(text="📍 Рядом со мной", callback_data="find:nearby")],
            [InlineKeyboardButton(text="🏠 В меню", callback_data="find:menu")],
        ]
    )


def category_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=category, callback_data=f"category:{category}")]
            for category in CATEGORIES
        ]
    )


def price_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=level, callback_data=f"price:{level}")]
            for level in PRICE_LEVELS
        ]
    )


def rating_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=label, callback_data=f"rating:{label}")]
            for label, _ in MIN_RATINGS
        ]
    )


def place_actions(place_id: int, is_favorite: bool) -> InlineKeyboardMarkup:
    favorite_text = "❤️ В избранном" if is_favorite else "🤍 В избранное"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=favorite_text, callback_data=f"place:{place_id}:favorite"
                ),
                InlineKeyboardButton(text="➡️ Следующее", callback_data="place:next"),
            ],
            [
                InlineKeyboardButton(text="💬 Читать отзывы", callback_data=f"place:{place_id}:reviews"),
                InlineKeyboardButton(text="📍 Адрес", callback_data=f"place:{place_id}:address"),
            ],
            [
                InlineKeyboardButton(text="👍", callback_data=f"place:{place_id}:like"),
                InlineKeyboardButton(text="👎", callback_data=f"place:{place_id}:dislike"),
            ],
            [InlineKeyboardButton(text="🏠 В меню", callback_data="place:menu")],
        ]
    )


def admin_moderation_keyboard(place_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Одобрить", callback_data=f"moderate:{place_id}:approve"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=f"moderate:{place_id}:reject"),
            ]
        ]
    )
