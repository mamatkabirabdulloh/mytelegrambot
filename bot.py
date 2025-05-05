from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import logging





API_TOKEN = '8055312415:AAFXSSsIYkv2kZUbIdlb8SSfQFvxU4u6Mnk'  # Bot tokeningni bu yerga qo‘y
ADMIN_ID = 447627974  # Bu yerga admin Telegram ID yozing

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)




# Har bir foydalanuvchining savatchasi
user_carts = {}

# FSM holatlari
class OrderState(StatesGroup):
    waiting_for_phone = State()
    waiting_for_location = State()

# Mahsulotlar ro‘yxati
products = {
    "Vibro Izoliyatsiya": {
        "Start 2mm": "28,000 so'm",
        "Noise Off 2mm": "31,000 so'm",
        "Audio 2mm": "30,000 so'm",
        "Bee 2mm": "40,000 so'm",
        "Astro 2mm": "40,000 so'm",
        "Start 3mm": "35,000 so'm",
        "Noise Off 3mm": "38,000 so'm",
        "Bee 3mm": "48,000 so'm",
        "Astro 3mm": "45,000 so'm",
    },
    "Issiqlik Izoliyatsiyasi": {
        "Fusion": "23,000 so'm",
        "Vision": "26,000 so'm",
        "Tishina": "28,000 so'm",
        "Accent": "30,000 so'm",
        "Splen": "32,000 so'm",
    },
    "Shovqindan Izoliyatsiya": {
        "Relief Standart": "22,000 so'm",
        "Relief Premium": "27,000 so'm",
    },
    "Carpet": {
        "Carpet 1": "33,000 so'm",
        "Carpet 2": "38,000 so'm",
    },
    "Vatin": {
        "Vatin 1": "12,000 so'm",
        "Vatin 2": "15,000 so'm",
    }
}

# /start komandasi
@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*products.keys(), "🛒 Savatni ko‘rish")
    await message.answer("Assalomu alaykum!\nNoise Off do‘koniga xush kelibsiz!\nMahsulot bo‘limini tanlang:", reply_markup=keyboard)

# Bo‘lim tanlash
@dp.message_handler(lambda message: message.text in products)
async def category_handler(message: types.Message):
    category = message.text
    for name, price in products[category].items():
        btn = InlineKeyboardMarkup()
        btn.add(InlineKeyboardButton(text="➕ Savatga qo‘shish", callback_data=f"add_{name}"))
        await message.answer(f"• {name} — {price}", reply_markup=btn)

# Mahsulotni savatga qo‘shish
@dp.callback_query_handler(lambda c: c.data.startswith("add_"))
async def add_to_cart(callback: types.CallbackQuery):
    product_name = callback.data[4:]
    user_id = callback.from_user.id
    if user_id not in user_carts:
        user_carts[user_id] = []
    user_carts[user_id].append(product_name)
    await callback.answer("Savatga qo‘shildi!")

# Savatni ko‘rish
@dp.message_handler(lambda message: message.text == "🛒 Savatni ko‘rish")
async def view_cart(message: types.Message):
    user_id = message.from_user.id
    cart = user_carts.get(user_id, [])
    if not cart:
        await message.answer("Savat bo‘sh.")
        return

    text = "Savatdagi mahsulotlaringiz:\n\n"
    for item in cart:
        text += f"• {item}\n"

    btn = InlineKeyboardMarkup()
    btn.add(InlineKeyboardButton("✅ Buyurtma berish", callback_data="order_now"))
    await message.answer(text, reply_markup=btn)

# Buyurtma boshlash
@dp.callback_query_handler(lambda c: c.data == "order_now")
async def start_order(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Telefon raqamingizni yuboring:", reply_markup=ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True
    ).add(KeyboardButton("📱 Raqamni yuborish", request_contact=True)))
    await OrderState.waiting_for_phone.set()
    await callback.answer()

# Telefon raqamini qabul qilish
@dp.message_handler(content_types=types.ContentType.CONTACT, state=OrderState.waiting_for_phone)
async def get_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    await message.answer("Manzilingizni yuboring:", reply_markup=ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True
    ).add(KeyboardButton("📍 Lokatsiyani yuborish", request_location=True)))
    await OrderState.waiting_for_location.set()

# Lokatsiyani qabul qilish
@dp.message_handler(content_types=types.ContentType.LOCATION, state=OrderState.waiting_for_location)
async def get_location(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    phone = user_data['phone']
    user_id = message.from_user.id
    cart = user_carts.get(user_id, [])
    if not cart:
        await message.answer("Savat bo‘sh.")
        return

    order_text = "Yangi buyurtma:\n"
    order_text += f"👤 Foydalanuvchi: @{message.from_user.username or 'No username'} (ID: {user_id})\n"
    order_text += f"📱 Telefon: {phone}\n"
    order_text += f"📍 Manzil: https://maps.google.com/?q={message.location.latitude},{message.location.longitude}\n\n"
    order_text += "🛒 Mahsulotlar:\n" + "\n".join(f"• {item}" for item in cart)

    await bot.send_message(chat_id=ADMIN_ID, text=order_text)
    await message.answer("Buyurtmangiz qabul qilindi!", reply_markup=ReplyKeyboardRemove())
    user_carts[user_id] = []
    await state.finish()


if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
    
    



    
