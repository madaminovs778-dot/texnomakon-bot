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
    "D2_S2": {"j": "A: Chuqur tozalash", "next": "WAIT_D3", "q": "🎉 2-dars tugadi! 3-dars ertaga ochiladi.", "kb": [], "d": "d2"},
    
    "D3_S1": {"j": "A: 4 marta ko'p piksel", "next": "D3_S2", "q": "❓ 3.2: OLED ekranning asosiy plyusi?", "kb": ["A: Haqiqiy qora rang", "B: Arzonligi"], "d": "d3"},
    "D3_S2": {"j": "A: Haqiqiy qora rang", "next": "WAIT_D4", "q": "✅ 3-dars tugadi! 4-dars ertaga ochiladi.", "kb": [], "d": "d3"},
    
    "D4_S1": {"j": "A: Mayda changni ushlash", "next": "D4_S2", "q": "❓ 4.2: Robot changyutgich datchigi?", "kb": ["A: Lidar/Lazer", "B: Oddiy chiroq"], "d": "d4"},
    "D4_S2": {"j": "A: Lidar/Lazer", "next": "WAIT_D5", "q": "✅ 4-dars tugadi! 5-dars ertaga ochiladi.", "kb": [], "d": "d4"},
    
    "D5_S1": {"j": "A: Tekis isitadi", "next": "D5_S2", "q": "❓ 5.2: Fenlardagi Ionizatsiya nima?", "kb": ["A: Sochni elektrlanishdan saqlaydi", "B: Tezroq quritadi"], "d": "d5"},
    "D5_S2": {"j": "A: Sochni elektrlanishdan saqlaydi", "next": "FINISH", "q": "🏁 Kurs yakunlandi!", "kb": [], "d": "d5"}
}

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    uid = str(message.from_user.id)
    data = load_data()
    bugun = datetime.now().strftime("%Y-%m-%d")
    
    if uid not in data:
        data[uid] = {"name": "Noma'lum", "step": "ISM_FAMILIYA", "errors": {"d1":0,"d2":0,"d3":0,"d4":0,"d5":0}, "last_done_date": ""}
    
    user = data[uid]

    # Kunlik cheklov tekshiruvi
    if user["last_done_date"] == bugun:
        await message.answer("⏳ Siz bugun darslarni bajarib bo'ldingiz. Keyingi dars ertaga ochiladi!")
        return

    save_data(data)
    
    if user["step"] == "WAIT_D3":
        user["step"] = "D3_S1"
        await message.answer("👋 Xush kelibsiz! Bugun 3-darsni boshlaymiz.")
        await message.answer(f"❓ 3.1: 4K va Full HD farqi?", reply_markup=get_kb(["A: 4 marta ko'p piksel", "B: Ovoz balandligi"]))
    elif user["step"] == "WAIT_D4":
        user["step"] = "D4_S1"
        await message.answer("👋 Xush kelibsiz! Bugun 4-darsni boshlaymiz.")
        await message.answer(f"❓ 4.1: HEPA filtr nima uchun?", reply_markup=get_kb(["A: Mayda changni ushlash", "B: Shovqinni kamaytirish"]))
    elif user["step"] == "WAIT_D5":
        user["step"] = "D5_S1"
        await message.answer("👋 Xush kelibsiz! Bugun 5-darsni boshlaymiz.")
        await message.answer(f"❓ 5.1: Mikroto'lqinli pechda Invertor nima qiladi?", reply_markup=get_kb(["A: Tekis isitadi", "B: Faqat yoritadi"]))
    elif user["step"] == "FINISH":
        await message.answer("🏁 Siz barcha darslarni tugatgansiz!")
    else:
        user["step"] = "ISM_FAMILIYA"
        await message.answer("Texnomakon o'quv botiga xush kelibsiz! 😊 Ism-familiyangizni kiriting:")
    
    save_data(data)

@dp.message_handler()
async def handle_message(message: types.Message):
    uid = str(message.from_user.id)
    txt = message.text
    data = load_data()
    if uid not in data: return
    user = data[uid]
    bugun = datetime.now().strftime("%Y-%m-%d")

    if user["step"] == "ISM_FAMILIYA":
        user["name"] = txt
        user["step"] = "D1_S1"
        save_data(data)
        await message.answer(f"Rahmat! 1-dars boshlandi.")
        await message.answer("❓ 1.1: Invertor motorning afzalligi nima?", reply_markup=get_kb(["A: Tezroq muzlatadi", "B: Elektrni tejaydi va shovqinsiz"]))
        return

    step = user["step"]
    if step in SAVOLLAR:
        if txt == SAVOLLAR[step]["j"]:
            user["step"] = SAVOLLAR[step]["next"]
            
            if "WAIT" in user["step"]:
                user["last_done_date"] = bugun
                save_data(data)
                from aiogram.types import ReplyKeyboardRemove
                await message.answer(f"✅ To'g'ri! {SAVOLLAR[step]['q']}\n\nKeyingi dars ertaga ochiladi.", reply_markup=ReplyKeyboardRemove())
            elif user["step"] == "FINISH":
                user["last_done_date"] = bugun
                save_data(data)
                jami_xato = sum(user["errors"].values())
                await bot.send_message(ADMIN_ID, f"🔔 NATIJA\n👤 Xodim: {user['name']}\n🏆 Kurs yakunlandi. Xatolar: {jami_xato}")
                from aiogram.types import ReplyKeyboardRemove
                await message.answer("🏁 Tabriklaymiz! Kursni to'liq tugatdingiz.", reply_markup=ReplyKeyboardRemove())
            else:
                save_data(data)
                kb = get_kb(SAVOLLAR[user["step"]]["kb"]) if SAVOLLAR[user["step"]]["kb"] else None
                await message.answer(f"✅ To'g'ri!\n\n{SAVOLLAR[user['step']]['q']}", reply_markup=kb)
        else:
            user["errors"][SAVOLLAR[step]["d"]] += 1
            save_data(data)
            await message.answer("❌ Xato! Yana urinib ko'ring:")

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
