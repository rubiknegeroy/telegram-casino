import asyncio
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ContentType
from config import TOKEN, ADMIN_ID, WEBAPP_URL
from database import get_balance, add_balance, remove_balance, cursor, conn

bot = Bot(TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()

# ---------- START ----------
@router.message(F.text == "/start")
async def start(msg: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎰 Казино", web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton(text="💰 Пополнить", callback_data="add_balance")],
        [InlineKeyboardButton(text="💼 Баланс", callback_data="check_balance")]
    ])
    await msg.answer("Добро пожаловать в StarsCasino!", reply_markup=kb)

# ---------- Пополнение ----------
@router.callback_query(F.data == "add_balance")
async def add_balance_handler(callback: CallbackQuery):
    add_balance(callback.from_user.id, 10)
    await callback.message.answer("Баланс пополнен на 10 ⭐")

# ---------- Проверка баланса ----------
@router.callback_query(F.data == "check_balance")
async def check_balance(callback: CallbackQuery):
    bal = get_balance(callback.from_user.id)
    await callback.message.answer(f"Ваш баланс: {bal} ⭐")

# ---------- Админка ----------
@router.message(F.text == "/admin")
async def admin_menu(msg: Message):
    if msg.from_user.id != ADMIN_ID:
        return await msg.answer("Нет доступа 🚫")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎁 Редактор подарков", callback_data="edit_gifts")],
        [InlineKeyboardButton(text="🎰 Редактор кейсов", callback_data="edit_cases")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="stats")]
    ])
    await msg.answer("Админ-панель:", reply_markup=kb)

dp.include_router(router)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
