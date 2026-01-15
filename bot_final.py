import asyncio
import logging
import json
import os
import time
from datetime import datetime
from aiogram import Bot, Dispatcher, types

# --- ASOSIY SOZLAMALAR ---
API_TOKEN = '8440984794:AAERxu45Si3ZEMegFbwVZCdMgFb63CqWfRM'
ADMIN_ID = 8478371721 
DB_FILE = "xodimlar_natijasi.json"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_kb(options):
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=opt)] for opt in options], resize_keyboard=True)

# SAVOLLAR BAZASI
SAVOLLAR = {
    "D1_S1": {"j": "B: Elektrni tejaydi va shovqinsiz", "next": "D1_S2", "q": "❓ 1.2: No Frost nima?", "kb": ["A: Muzlashni oldini oladi", "B: Suv tejaydi"], "d": "d1"},
    "D1_S2": {"j": "A: Muzlashni oldini oladi", "next": "D2_S1", "q": "✅ 1-dars tugadi!\n\n❓ 2.1: Steam funksiyasi nima?", "kb": ["A: Mikroblarni o'ldiradi", "B: Rangni o'zgartiradi"], "d": "d1"},
    "D2_S1": {"j": "A: Mikroblarni o'ldiradi", "next": "D2_S2", "q": "❓ 2.2: Eco Bubble nima?", "kb": ["A: Chuqur tozalash", "B: Ko'p suv sarfi"], "d": "d2"},
    "D2_S2": {"j": "A: Chuqur tozalash", "next": "D3_S1", "q": "✅ 2-dars tugadi!\n\n❓ 3.1: 4K va Full HD farqi?", "kb": ["A: 4 marta ko'p piksel", "B: Ovoz balandligi"], "d": "d2"},
    "D3_S1": {"j": "A: 4 marta ko'p piksel", "next": "D3_S2", "q": "❓ 3.2: OLED ekranning asosiy plyusi?", "kb": ["A: Haqiqiy qora rang", "B: Arzonligi"], "d": "d3"},
    "D3_S2": {"j": "A: Haqiqiy qora rang", "next": "D4_S1", "q": "✅ 3-dars tugadi!\n\n❓ 4.1: HEPA filtr nima uchun?", "kb": ["A: Mayda changni ushlash", "B: Shovqinni kamaytirish"], "d": "d3"},
    "D4_S1": {"j": "A: Mayda changni ushlash", "next": "D4_S2", "q": "❓ 4.2: Robot changyutgich datchigi?", "kb": ["A: Lidar/Lazer", "B: Oddiy chiroq"], "d": "d4"},
    "D4_S2": {"j": "A: Lidar/Lazer", "next": "D5_S1", "q": "✅ 4-dars tugadi!\n\n❓ 5.1: Mikroto'lqinli pechda Invertor nima qiladi?", "kb": ["A: Tekis isitadi", "B: Faqat yoritadi"], "d": "d4"},
    "D5_S1": {"j": "A: Tekis isitadi", "next": "D5_S2", "q": "❓ 5.2: Fenlardagi Ionizatsiya nima?", "kb": ["A: Sochni elektrlanishdan saqlaydi", "B: Tezroq quritadi"], "d": "d5"},
    "D5_S2": {"j": "A: Sochni elektrlanishdan saqlaydi", "next": "FINISH", "q": "🏁 Kurs yakunlandi!", "kb": [], "d": "d5"}
}

async def auto_timer(chat_id, user_id, step_at_start):
    await asyncio.sleep(30) # 30 soniya kutish
    data = load_data()
    uid = str(user_id)
    if uid in data and data[uid]["step"] == step_at_start:
        user = data[uid]
        d_key = SAVOLLAR[step_at_start]["d"]
        user["errors"][d_key] += 1
        user["step"] = SAVOLLAR[step_at_start]["next"]
        save_data(data)
        
        await bot.send_message(chat_id, "⏰ Vaqtingiz tugadi! Bu xato deb hisoblandi.")
        
        if user["step"] == "FINISH":
            await bot.send_message(chat_id, "🏁 Kurs yakunlandi!")
        else:
            kb = get_kb(SAVOLLAR[user["step"]]["kb"]) if SAVOLLAR[user["step"]]["kb"] else None
            await bot.send_message(chat_id, f"Keyingi savol:\n\n{SAVOLLAR[user['step']]['q']}", reply_markup=kb)
            asyncio.create_task(auto_timer(chat_id, user_id, user["step"]))

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    uid = str(message.from_user.id)
    data = load_data()
    data[uid] = {
        "name": "Noma'lum", "step": "ISM_FAMILIYA", 
        "errors": {"d1": 0, "d2": 0, "d3": 0, "d4": 0, "d5": 0}
    }
    save_data(data)
    await message.answer("Texnomakon o'quv botiga xush kelibsiz! 😊\n\nIsm va Familiyangizni kiriting:")

@dp.message_handler()
async def handle_message(message: types.Message):
    uid = str(message.from_user.id)
    txt = message.text
    data = load_data()
    if uid not in data: return
    user = data[uid]

    if user["step"] == "ISM_FAMILIYA":
        user["name"] = txt
        user["step"] = "D1_S1"
        save_data(data)
        await message.answer(f"Rahmat, {txt}! 1-dars boshlandi. Har bir savolga 30 soniya beriladi!")
        await message.answer("❓ 1.1: Invertor motorning afzalligi nima?", 
                             reply_markup=get_kb(["A: Tezroq muzlatadi", "B: Elektrni tejaydi va shovqinsiz"]))
        asyncio.create_task(auto_timer(message.chat.id, message.from_user.id, "D1_S1"))
        return

    step = user["step"]
    if step in SAVOLLAR:
        if txt == SAVOLLAR[step]["j"]:
            user["step"] = SAVOLLAR[step]["next"]
            save_data(data)
            if user["step"] == "FINISH":
                jami_xato = sum(user["errors"].values())
                await bot.send_message(ADMIN_ID, f"🔔 YANGI NATIJA\n👤 Xodim: {user['name']}\n❌ Xatolar: {jami_xato}")
                from aiogram.types import ReplyKeyboardRemove
                await message.answer("🏁 Tabriklaymiz! Kurs tugadi.", reply_markup=ReplyKeyboardRemove())
            else:
                kb = get_kb(SAVOLLAR[user["step"]]["kb"]) if SAVOLLAR[user["step"]]["kb"] else None
                await message.answer(f"✅ To'g'ri!\n\n{SAVOLLAR[user['step']]['q']}", reply_markup=kb)
                asyncio.create_task(auto_timer(message.chat.id, message.from_user.id, user["step"]))
        else:
            await message.answer("❌ Xato! Yana urinib ko'ring (vaqt ketyapti):")

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
