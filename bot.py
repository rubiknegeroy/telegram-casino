import asyncio
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.enums import ContentType
from database import cursor, conn, get_balance, add_balance, remove_balance

TOKEN = "7702115093:AAG33V5LgsgOXnwGAhP5MRmJa1jSj78PUwk"
ADMIN_ID = 5827986904  # твой ID

bot = Bot(TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()

# ---------- FSM ----------
class GiftState(StatesGroup):
    name = State()
    emoji = State()
    rarity = State()
    image = State()

class CaseState(StatesGroup):
    name = State()
    price = State()
    image = State()

class CaseGiftState(StatesGroup):
    case_id = State()
    gift_id = State()
    chance = State()

# ---------- START ----------
@router.message(F.text == "/start")
async def start(msg: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎰 Казино", web_app={"url": "https://rubiknegeroy.github.io/telegram-casino/index.html"})],
        [InlineKeyboardButton(text="💰 Пополнить баланс", callback_data="add_balance")]
    ])
    await msg.answer("Добро пожаловать в StarsCasino!", reply_markup=kb)

# ---------- Пополнение ----------
@router.callback_query(F.data == "add_balance")
async def add_balance_handler(callback: CallbackQuery):
    await callback.message.answer("Введите сумму пополнения (⭐):")
    await callback.answer()

@router.message(F.text.regexp(r'^\d+$'))
async def process_balance_input(msg: Message):
    amount = int(msg.text)
    add_balance(msg.from_user.id, amount)
    await msg.answer(f"Баланс пополнен на {amount} ⭐")

# ---------- Баланс ----------
@router.message(F.text == "/balance")
async def balance(msg: Message):
    bal = get_balance(msg.from_user.id)
    await msg.answer(f"Ваш баланс: {bal} ⭐")

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

# ---------- Подарки ----------
@router.callback_query(F.data == "edit_gifts")
async def edit_gifts(callback: CallbackQuery):
    cursor.execute("SELECT id, name, emoji, rarity FROM gifts")
    gifts = cursor.fetchall()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{g[1]} {g[2]} ({g[3]})", callback_data=f"edit_gift_{g[0]}")] for g in gifts
    ] + [[InlineKeyboardButton(text="➕ Добавить подарок", callback_data="add_gift")]])
    
    await callback.message.answer("🎁 Список подарков:", reply_markup=kb)

@router.callback_query(F.data == "add_gift")
async def add_gift_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(GiftState.name)
    await callback.message.answer("Введите название подарка:")

@router.message(GiftState.name)
async def add_gift_name(msg: Message, state: FSMContext):
    await state.update_data(name=msg.text)
    await state.set_state(GiftState.emoji)
    await msg.answer("Отправьте эмодзи подарка:")

@router.message(GiftState.emoji)
async def add_gift_emoji(msg: Message, state: FSMContext):
    await state.update_data(emoji=msg.text)
    await state.set_state(GiftState.rarity)
    await msg.answer("Введите редкость (обычный/редкий/легендарный):")

@router.message(GiftState.rarity)
async def add_gift_rarity(msg: Message, state: FSMContext):
    await state.update_data(rarity=msg.text)
    await state.set_state(GiftState.image)
    await msg.answer("Отправьте фото подарка:")

@router.message(GiftState.image, F.content_type == ContentType.PHOTO)
async def add_gift_image(msg: Message, state: FSMContext):
    file_id = msg.photo[-1].file_id
    data = await state.get_data()
    
    cursor.execute("INSERT INTO gifts (name, emoji, rarity, image) VALUES (?, ?, ?, ?)",
                   (data["name"], data["emoji"], data["rarity"], file_id))
    conn.commit()
    
    await state.clear()
    await msg.answer("🎁 Подарок добавлен ✅")

@router.callback_query(F.data.startswith("edit_gift_"))
async def edit_single_gift(callback: CallbackQuery):
    gift_id = int(callback.data.split("_")[2])
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗑 Удалить подарок", callback_data=f"delete_gift_{gift_id}")]
    ])
    await callback.message.answer(f"Редактирование подарка ID {gift_id}:", reply_markup=kb)

@router.callback_query(F.data.startswith("delete_gift_"))
async def delete_gift(callback: CallbackQuery):
    gift_id = int(callback.data.split("_")[2])
    cursor.execute("DELETE FROM gifts WHERE id=?", (gift_id,))
    cursor.execute("DELETE FROM case_gifts WHERE gift_id=?", (gift_id,))
    conn.commit()
    await callback.message.answer("🗑 Подарок удалён ✅")

# ---------- Кейсы ----------
@router.callback_query(F.data == "edit_cases")
async def edit_cases(callback: CallbackQuery):
    cursor.execute("SELECT id, name, price FROM cases")
    cases = cursor.fetchall()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{c[1]} ({c[2]} ⭐)", callback_data=f"edit_case_{c[0]}")] for c in cases
    ] + [[InlineKeyboardButton(text="➕ Создать кейс", callback_data="add_case")]])
    
    await callback.message.answer("🎰 Список кейсов:", reply_markup=kb)

@router.callback_query(F.data == "add_case")
async def add_case_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CaseState.name)
    await callback.message.answer("Введите название кейса:")

@router.message(CaseState.name)
async def add_case_name(msg: Message, state: FSMContext):
    await state.update_data(name=msg.text)
    await state.set_state(CaseState.price)
    await msg.answer("Введите цену кейса (⭐):")

@router.message(CaseState.price)
async def add_case_price(msg: Message, state: FSMContext):
    await state.update_data(price=int(msg.text))
    await state.set_state(CaseState.image)
    await msg.answer("Отправьте фото кейса:")

@router.message(CaseState.image, F.content_type == ContentType.PHOTO)
async def add_case_image(msg: Message, state: FSMContext):
    file_id = msg.photo[-1].file_id
    data = await state.get_data()
    
    cursor.execute("INSERT INTO cases (name, price, image) VALUES (?, ?, ?)",
                   (data["name"], data["price"], file_id))
    conn.commit()
    
    await state.clear()
    await msg.answer("🎰 Кейс добавлен ✅")

@router.callback_query(F.data.startswith("edit_case_"))
async def edit_single_case(callback: CallbackQuery):
    case_id = int(callback.data.split("_")[2])
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎁 Добавить подарок", callback_data=f"add_gift_to_case_{case_id}")],
        [InlineKeyboardButton(text="🗑 Удалить кейс", callback_data=f"delete_case_{case_id}")]
    ])
    await callback.message.answer(f"Редактирование кейса ID {case_id}:", reply_markup=kb)

@router.callback_query(F.data.startswith("delete_case_"))
async def delete_case(callback: CallbackQuery):
    case_id = int(callback.data.split("_")[2])
    cursor.execute("DELETE FROM cases WHERE id=?", (case_id,))
    cursor.execute("DELETE FROM case_gifts WHERE case_id=?", (case_id,))
    conn.commit()
    await callback.message.answer("🗑 Кейс удалён ✅")

# ---------- Привязка подарков ----------
@router.callback_query(F.data.startswith("add_gift_to_case_"))
async def add_gift_to_case(callback: CallbackQuery, state: FSMContext):
    case_id = int(callback.data.split("_")[4])
    await state.update_data(case_id=case_id)

    cursor.execute("SELECT id, name FROM gifts")
    gifts = cursor.fetchall()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{g[1]}", callback_data=f"select_gift_{g[0]}")] for g in gifts
    ])
    await callback.message.answer("Выберите подарок для добавления:", reply_markup=kb)

@router.callback_query(F.data.startswith("select_gift_"))
async def select_gift_for_case(callback: CallbackQuery, state: FSMContext):
    gift_id = int(callback.data.split("_")[2])
    await state.update_data(gift_id=gift_id)
    await state.set_state(CaseGiftState.chance)
    await callback.message.answer("Введите шанс выпадения (в %):")

@router.message(CaseGiftState.chance)
async def save_gift_chance(msg: Message, state: FSMContext):
    data = await state.get_data()
    chance = int(msg.text)

    cursor.execute("INSERT INTO case_gifts (case_id, gift_id, chance) VALUES (?, ?, ?)",
                   (data["case_id"], data["gift_id"], chance))
    conn.commit()

    await state.clear()
    await msg.answer("🎁 Подарок успешно добавлен в кейс ✅")

# ---------- Подключаем роутер ----------
dp.include_router(router)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
