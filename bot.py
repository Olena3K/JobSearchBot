import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from parser import search_workua_jobs

# Завантаження змінних із .env
load_dotenv()

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("bot.log")],
)
logger = logging.getLogger(__name__)

# Завантаження токена
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    logger.error("Токен бота не знайдено!")
    raise ValueError("Токен бота не задано.")

bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)


# Створення Reply Keyboard з готовими запитами
def get_search_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Python"), KeyboardButton(text="Продавець")],
            [KeyboardButton(text="Менеджер"), KeyboardButton(text="Дизайнер")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    return keyboard


@router.message(F.text == "/start")
async def send_welcome(message: Message):
    logger.info(f"Отримано команду /start від користувача {message.from_user.id}")
    builder = InlineKeyboardBuilder()
    builder.button(text="🔍 Пошук вакансій", callback_data="search_jobs")
    builder.button(text="ℹ️ Про бота", callback_data="about")
    await message.answer(
        "👋 Оберіть опцію:",
        reply_markup=builder.as_markup(),  # Тільки inline-клавіатура
    )


@router.callback_query(F.data == "search_jobs")
async def search_prompt(callback: CallbackQuery):
    logger.info(f"Користувач {callback.from_user.id} вибрав пошук вакансій")
    await callback.message.answer(
        "Введіть назву професії або оберіть із запропонованих:",
        reply_markup=get_search_keyboard(),  # Reply Keyboard для запитів
    )
    await callback.answer()


@router.callback_query(F.data == "about")
async def send_help(callback: CallbackQuery):
    logger.info(f"Користувач {callback.from_user.id} запросив інформацію про бота")
    text = (
        "🤖 *SmartJobAlertsBot* — це бот, який допомагає тобі знаходити вакансії швидко й зручно.\n\n"
        "🔎 Просто обери пошук, введи бажану професію або технологію, і бот надасть посилання на вакансії з Work.ua.\n"
        "🛠 У майбутньому буде додано більше сайтів і фільтрів для якіснішого пошуку.))"
    )
    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()


@router.message(F.text == "/status")
async def status(message: Message):
    logger.info(f"Отримано команду /status від користувача {message.from_user.id}")
    await message.answer("🤖 Бот активний і готовий до роботи!")


@router.message()
async def handle_query(message: Message):
    logger.info(
        f"Отримано запит на пошук вакансій: '{message.text}' від користувача {message.from_user.id}"
    )
    await message.answer("🔎 Шукаю вакансії...")
    try:
        results = search_workua_jobs(message.text)
        await message.answer("\n\n".join(results), reply_markup=get_search_keyboard())
    except Exception as e:
        logger.error(f"Помилка під час пошуку вакансій: {e}")
        await message.answer(
            "⚠️ Виникла помилка під час пошуку. Спробуйте ще раз.",
            reply_markup=get_search_keyboard(),
        )


async def main():
    logger.info("Запуск бота...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Помилка під час роботи бота: {e}")


if __name__ == "__main__":
    asyncio.run(main())
