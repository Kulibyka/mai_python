from __future__ import annotations

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from tg.app.keyboards import (
    MAIN_MENU,
    MIN_RATINGS,
    category_keyboard,
    find_menu,
    place_actions,
    price_keyboard,
    rating_keyboard,
)
from tg.app.models import Place, utc_now
from tg.app.services import LlmSummaryService, RecommendationService, SearchFilters
from tg.app.states import AddPlaceStates, SearchStates
from tg.app.storage import JsonStorage

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    text = (
        "Привет! 👋 Я твой личный гид по интересным местам.\n"
        "Помогу найти куда сходить сегодня вечером или на выходных.\n"
        "Я учитываю твои вкусы и мнение других пользователей. Что хочешь сделать?"
    )
    await message.answer(text, reply_markup=MAIN_MENU)


@router.message(Command("menu"))
async def menu_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Главное меню", reply_markup=MAIN_MENU)


@router.message(F.text == "🎯 Найти место")
async def find_place(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Вы ищете что-то конкретное или хотите рекомендацию?",
        reply_markup=find_menu(),
    )


@router.callback_query(F.data == "find:menu")
async def find_back_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.answer("Главное меню", reply_markup=MAIN_MENU)
    await callback.answer()


@router.callback_query(F.data == "find:category")
async def find_category(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(SearchStates.category)
    await callback.message.edit_text("Выберите категорию:", reply_markup=category_keyboard())
    await callback.answer()


@router.callback_query(F.data == "find:search")
async def find_search(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(SearchStates.query)
    await callback.message.edit_text("Введите текст для поиска:")
    await callback.answer()


@router.callback_query(F.data == "find:random")
async def find_random(callback: CallbackQuery, storage: JsonStorage, llm: LlmSummaryService) -> None:
    recommender = RecommendationService()
    place = recommender.random_place(storage.list_places())
    if place is None:
        await callback.message.edit_text("Пока нет одобренных мест. Попробуйте позже.")
        await callback.answer()
        return
    await send_place_card(callback.message, place, storage, llm)
    await callback.answer()


@router.callback_query(F.data == "find:nearby")
async def find_nearby(callback: CallbackQuery) -> None:
    await callback.message.answer(
        "Функция геопоиска появится позже. Пока рекомендую выбрать категорию 😉"
    )
    await callback.answer()


@router.callback_query(SearchStates.category, F.data.startswith("category:"))
async def select_category(callback: CallbackQuery, state: FSMContext) -> None:
    category = callback.data.split(":", 1)[1]
    await state.update_data(category=category)
    await state.set_state(SearchStates.price)
    await callback.message.edit_text("Выберите ценовой диапазон:", reply_markup=price_keyboard())
    await callback.answer()


@router.callback_query(SearchStates.price, F.data.startswith("price:"))
async def select_price(callback: CallbackQuery, state: FSMContext) -> None:
    price = callback.data.split(":", 1)[1]
    await state.update_data(price=price)
    await state.set_state(SearchStates.rating)
    await callback.message.edit_text("Минимальный рейтинг:", reply_markup=rating_keyboard())
    await callback.answer()


@router.callback_query(SearchStates.rating, F.data.startswith("rating:"))
async def select_rating(
    callback: CallbackQuery,
    state: FSMContext,
    storage: JsonStorage,
    llm: LlmSummaryService,
) -> None:
    label = callback.data.split(":", 1)[1]
    rating_value = next((value for item, value in MIN_RATINGS if item == label), None)
    data = await state.get_data()
    filters = SearchFilters(
        category=data.get("category"),
        price_level=data.get("price"),
        min_rating=rating_value,
    )
    recommender = RecommendationService()
    results = recommender.filter_places(storage.list_places(), filters)
    if not results:
        await callback.message.edit_text("Ничего не найдено. Попробуйте другую категорию.")
        await state.clear()
        await callback.answer()
        return
    await state.update_data(results=[place.id for place in results], index=0)
    await state.set_state(SearchStates.rating)
    await send_place_card(callback.message, results[0], storage, llm)
    await callback.answer()


@router.message(SearchStates.query)
async def handle_query(
    message: Message,
    state: FSMContext,
    storage: JsonStorage,
    llm: LlmSummaryService,
) -> None:
    query = message.text.strip()
    filters = SearchFilters(query=query)
    recommender = RecommendationService()
    results = recommender.filter_places(storage.list_places(), filters)
    if not results:
        await message.answer("Ничего не найдено. Попробуйте другой запрос.")
        await state.clear()
        return
    await state.update_data(results=[place.id for place in results], index=0)
    await send_place_card(message, results[0], storage, llm)


async def send_place_card(
    message: Message,
    place: Place,
    storage: JsonStorage,
    llm: LlmSummaryService,
) -> None:
    reviews = storage.list_reviews(place.id, status="approved")
    summary = llm.summarize(place, reviews)
    is_favorite = place.id in storage.get_profile(message.chat.id).favorites
    text = (
        f"*{place.name}*\n"
        f"Категория: {place.category}\n"
        f"Цена: {place.price_level}\n"
        f"Рейтинг: {place.rating:.1f}\n\n"
        f"{summary}"
    )
    await message.answer(text, reply_markup=place_actions(place.id, is_favorite), parse_mode=ParseMode.MARKDOWN)


@router.callback_query(F.data == "place:next")
async def next_place(
    callback: CallbackQuery,
    state: FSMContext,
    storage: JsonStorage,
    llm: LlmSummaryService,
) -> None:
    data = await state.get_data()
    results = data.get("results", [])
    if not results:
        await callback.message.answer("Сначала выберите категорию или поиск.")
        await callback.answer()
        return
    index = int(data.get("index", 0)) + 1
    if index >= len(results):
        await callback.message.answer("Это все варианты. Попробуйте другие фильтры.")
        await state.clear()
        await callback.answer()
        return
    await state.update_data(index=index)
    place = storage.get_place(results[index])
    if place:
        await send_place_card(callback.message, place, storage, llm)
    await callback.answer()


@router.callback_query(F.data.startswith("place:") & F.data.endswith(":favorite"))
async def toggle_favorite(callback: CallbackQuery, storage: JsonStorage) -> None:
    _, place_id, _ = callback.data.split(":")
    is_favorite = storage.toggle_favorite(callback.from_user.id, int(place_id))
    text = "Добавлено в избранное." if is_favorite else "Удалено из избранного."
    await callback.message.answer(text)
    await callback.answer()


@router.callback_query(F.data.startswith("place:") & F.data.endswith(":reviews"))
async def show_reviews(callback: CallbackQuery, storage: JsonStorage) -> None:
    _, place_id, _ = callback.data.split(":")
    reviews = storage.list_reviews(int(place_id), status="approved")
    if not reviews:
        await callback.message.answer("Отзывов пока нет. Вы можете стать первым!")
        await callback.answer()
        return
    preview = "\n\n".join(
        f"⭐ {review.rating:.1f} — {review.text}" for review in reviews[:3]
    )
    await callback.message.answer(preview)
    await callback.answer()


@router.callback_query(F.data.startswith("place:") & F.data.endswith(":address"))
async def show_address(callback: CallbackQuery, storage: JsonStorage) -> None:
    _, place_id, _ = callback.data.split(":")
    place = storage.get_place(int(place_id))
    if place:
        await callback.message.answer(f"Адрес: {place.address}")
    await callback.answer()


@router.callback_query(F.data.startswith("place:") & F.data.endswith(":like"))
async def like_place(callback: CallbackQuery, storage: JsonStorage) -> None:
    _, place_id, _ = callback.data.split(":")
    storage.record_like(callback.from_user.id, int(place_id), 1)
    await callback.message.answer("Спасибо! Мы учтем ваш лайк в будущих рекомендациях.")
    await callback.answer()


@router.callback_query(F.data.startswith("place:") & F.data.endswith(":dislike"))
async def dislike_place(callback: CallbackQuery, storage: JsonStorage) -> None:
    _, place_id, _ = callback.data.split(":")
    storage.record_like(callback.from_user.id, int(place_id), -1)
    await callback.message.answer("Учтем ваш выбор. Подберем что-то другое!")
    await callback.answer()


@router.callback_query(F.data == "place:menu")
async def place_back_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.answer("Главное меню", reply_markup=MAIN_MENU)
    await callback.answer()


@router.message(F.text == "➕ Добавить место")
async def add_place_start(message: Message, state: FSMContext) -> None:
    await state.set_state(AddPlaceStates.name)
    await message.answer("Введите название места:")


@router.message(AddPlaceStates.name)
async def add_place_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text.strip())
    await state.set_state(AddPlaceStates.category)
    await message.answer("Выберите категорию:", reply_markup=category_keyboard())


@router.callback_query(AddPlaceStates.category, F.data.startswith("category:"))
async def add_place_category(callback: CallbackQuery, state: FSMContext) -> None:
    category = callback.data.split(":", 1)[1]
    await state.update_data(category=category)
    await state.set_state(AddPlaceStates.address)
    await callback.message.edit_text("Укажите адрес или отправьте геолокацию:")
    await callback.answer()


@router.message(AddPlaceStates.address)
async def add_place_address(message: Message, state: FSMContext) -> None:
    await state.update_data(address=message.text.strip())
    await state.set_state(AddPlaceStates.description)
    await message.answer("Опишите место или оставьте ссылку:")


@router.message(AddPlaceStates.description)
async def add_place_description(message: Message, state: FSMContext) -> None:
    await state.update_data(description=message.text.strip())
    await state.set_state(AddPlaceStates.price)
    await message.answer("Оцените по шкале цен:", reply_markup=price_keyboard())


@router.callback_query(AddPlaceStates.price, F.data.startswith("price:"))
async def add_place_price(callback: CallbackQuery, state: FSMContext) -> None:
    price = callback.data.split(":", 1)[1]
    await state.update_data(price=price)
    data = await state.get_data()
    summary = (
        "Проверьте информацию:\n"
        f"Название: {data.get('name')}\n"
        f"Категория: {data.get('category')}\n"
        f"Адрес: {data.get('address')}\n"
        f"Описание: {data.get('description')}\n"
        f"Цена: {data.get('price')}\n\n"
        "Все верно? Напишите: да / нет"
    )
    await state.set_state(AddPlaceStates.confirm)
    await callback.message.edit_text(summary)
    await callback.answer()


@router.message(AddPlaceStates.confirm)
async def add_place_confirm(
    message: Message,
    state: FSMContext,
    storage: JsonStorage,
) -> None:
    answer = message.text.strip().lower()
    if answer not in {"да", "нет"}:
        await message.answer("Пожалуйста, ответьте 'да' или 'нет'.")
        return
    if answer == "нет":
        await state.clear()
        await message.answer("Ок! Данные не сохранены.", reply_markup=MAIN_MENU)
        return
    data = await state.get_data()
    place = Place(
        id=storage.next_place_id(),
        name=data["name"],
        category=data["category"],
        address=data["address"],
        description=data["description"],
        price_level=data["price"],
        rating=0.0,
        status="pending",
        created_by=message.from_user.id,
        created_at=utc_now(),
    )
    storage.add_place(place)
    await state.clear()
    await message.answer(
        "Спасибо! Место отправлено на модерацию. После одобрения оно появится в каталоге.",
        reply_markup=MAIN_MENU,
    )


@router.message(F.text == "💬 Профиль")
async def profile_menu(message: Message, storage: JsonStorage) -> None:
    favorites = storage.list_favorites(message.from_user.id)
    user_places = storage.list_user_places(message.from_user.id)
    text = (
        f"❤️ Избранное: {len(favorites)} мест\n"
        f"➕ Добавленные места: {len(user_places)}\n"
        "Напишите 'избранное' или 'мои места' чтобы посмотреть списки."
    )
    await message.answer(text)


@router.message(F.text.lower() == "избранное")
async def show_favorites(message: Message, storage: JsonStorage) -> None:
    favorites = storage.list_favorites(message.from_user.id)
    if not favorites:
        await message.answer("Избранных мест пока нет.")
        return
    lines = [f"• {place.name} ({place.category})" for place in favorites]
    await message.answer("\n".join(lines))


@router.message(F.text.lower() == "мои места")
async def show_user_places(message: Message, storage: JsonStorage) -> None:
    places = storage.list_user_places(message.from_user.id)
    if not places:
        await message.answer("Вы еще не добавляли места.")
        return
    lines = [f"• {place.name} — {place.status}" for place in places]
    await message.answer("\n".join(lines))


@router.message(F.text == "🏆 Топы")
async def show_tops(message: Message, storage: JsonStorage, llm: LlmSummaryService) -> None:
    places = sorted(storage.list_places(status="approved"), key=lambda item: item.rating, reverse=True)
    if not places:
        await message.answer("Пока нет одобренных мест.")
        return
    await message.answer("Топ популярных мест:")
    for place in places[:3]:
        await send_place_card(message, place, storage, llm)


@router.message(F.text == "⚙️ Настройки и помощь")
async def settings_help(message: Message) -> None:
    text = (
        "Доступные команды:\n"
        "/menu — главное меню\n"
        "/admin — панель модерации (если вы админ)\n\n"
        "Если нужна помощь, напишите сюда описание проблемы."
    )
    await message.answer(text)


@router.message(Command("admin"))
async def admin_panel(message: Message, storage: JsonStorage, admin_ids: set[int]) -> None:
    if message.from_user.id not in admin_ids:
        await message.answer("У вас нет прав модератора.")
        return
    pending = storage.list_places(status="pending")
    if not pending:
        await message.answer("Нет мест на модерации.")
        return
    await message.answer("Места на модерации:")
    for place in pending:
        text = (
            f"{place.name}\n"
            f"Категория: {place.category}\n"
            f"Адрес: {place.address}\n"
            f"Описание: {place.description}\n"
            f"Цена: {place.price_level}"
        )
        from tg.app.keyboards import admin_moderation_keyboard

        await message.answer(text, reply_markup=admin_moderation_keyboard(place.id))


@router.callback_query(F.data.startswith("moderate:"))
async def moderate_place(callback: CallbackQuery, storage: JsonStorage, admin_ids: set[int]) -> None:
    if callback.from_user.id not in admin_ids:
        await callback.message.answer("Нет прав для модерации.")
        await callback.answer()
        return
    _, place_id, action = callback.data.split(":")
    place = storage.get_place(int(place_id))
    if not place:
        await callback.message.answer("Место не найдено.")
        await callback.answer()
        return
    if action == "approve":
        place.status = "approved"
    else:
        place.status = "rejected"
    storage.update_place(place)
    await callback.message.answer(f"Готово. Статус: {place.status}.")
    await callback.answer()


@router.message()
async def fallback(message: Message) -> None:
    await message.answer("Не понял команду. Используйте меню или /menu.")
