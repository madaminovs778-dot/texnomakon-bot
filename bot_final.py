import asyncio
import logging
import json
import os
import time
from datetime import datetime
from aiogram import Bot, Dispatcher, types, 
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

# --- ASOSIY SOZLAMALAR ---
API_TOKEN = '8440984794:AAERxu45Si3ZEMegFbwVZCdMgFb63CqWfRM'
ADMIN_ID = 8478371721  # Sizning ID raqamingiz
DB_FILE = "xodimlar_natijasi.json"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Ma'lumotlarni yuklash va saqlash
def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_kb(options):
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=opt)] for opt in options], resize_keyboard=True)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    uid = str(message.from_user.id)
    data = load_data()
    data[uid] = {
        "name": "Noma'lum", "step": "ISM_FAMILIYA", 
        "errors": {"d1": 0, "d2": 0, "d3": 0, "d4": 0, "d5": 0},
        "last_done_date": "", "q_start_time": 0
    }
    save_data(data)
    await message.answer("Texnomakon o'quv botiga xush kelibsiz! 😊\n\nIsm va Familiyangizni kiriting:", protect_content=True)

@dp.message()
async def handle_message(message: types.Message):
    uid = str(message.from_user.id)
    txt = message.text
    data = load_data()
    if uid not in data: return
    user = data[uid]
    bugun = datetime.now().strftime("%Y-%m-%d")

    # Ism familiya qabul qilish
    if user["step"] == "ISM_FAMILIYA":
        user["name"] = txt
        user["step"] = "D1_S1"
        user["q_start_time"] = time.time()
        save_data(data)
        await message.answer(f"Rahmat, {txt}! 1-dars boshlandi. Har bir savolga 30 soniya beriladi!", protect_content=True)
        await message.answer("❓ 1.1: Invertor motorning afzalligi nima?", 
                             reply_markup=get_kb(["A: Tezroq muzlatadi", "B: Elektrni tejaydi va shovqinsiz"]), protect_content=True)
        return

    # SAVOLLAR BAZASI (Barcha 5 ta dars)
    savollar = {
        # 1-DARS
        "D1_S1": {"j": "B: Elektrni tejaydi va shovqinsiz", "next": "D1_S2", "q": "❓ 1.2: No Frost nima?", "kb": ["A: Muzlashni oldini oladi", "B: Suv tejaydi"], "d": "d1"},
        "D1_S2": {"j": "A: Muzlashni oldini oladi", "next": "D2_S1", "q": "✅ 1-dars tugadi!\n\n🔹 2-DARS: Kir yuvish mashinalari.\n❓ 2.1: Steam funksiyasi nima?", "kb": ["A: Mikroblarni o'ldiradi", "B: Rangni o'zgartiradi"], "d": "d1"},
        
        # 2-DARS
        "D2_S1": {"j": "A: Mikroblarni o'ldiradi", "next": "D2_S2", "q": "❓ 2.2: Eco Bubble nima?", "kb": ["A: Chuqur tozalash", "B: Ko'p suv sarfi"], "d": "d2"},
        "D2_S2": {"j": "A: Chuqur tozalash", "next": "D3_S1", "q": "✅ 2-dars tugadi!\n\n🔹 3-DARS: Televizorlar.\n❓ 3.1: 4K va Full HD farqi?", "kb": ["A: 4 marta ko'p piksel", "B: Ovoz balandligi"], "d": "d2"},
        
        # 3-DARS
        "D3_S1": {"j": "A: 4 marta ko'p piksel", "next": "D3_S2", "q": "❓ 3.2: OLED ekranning asosiy plyusi?", "kb": ["A: Haqiqiy qora rang", "B: Arzonligi"], "d": "d3"},
        "D3_S2": {"j": "A: Haqiqiy qora rang", "next": "D4_S1", "q": "✅ 3-dars tugadi!\n\n🔹 4-DARS: Changyutgichlar.\n❓ 4.1: HEPA filtr nima uchun?", "kb": ["A: Mayda changni ushlash", "B: Shovqinni kamaytirish"], "d": "d3"},
        
        # 4-DARS
        "D4_S1": {"j": "A: Mayda changni ushlash", "next": "D4_S2", "q": "❓ 4.2: Robot changyutgich datchigi?", "kb": ["A: Lidar/Lazer", "B: Oddiy chiroq"], "d": "d4"},
        "D4_S2": {"j": "A: Lidar/Lazer", "next": "D5_S1", "q": "✅ 4-dars tugadi!\n\n🔹 5-DARS: Mayda texnika.\n❓ 5.1: Mikroto'lqinli pechda Invertor nima qiladi?", "kb": ["A: Tekis isitadi", "B: Faqat yoritadi"], "d": "d4"},
        
        # 5-DARS
        "D5_S1": {"j": "A: Tekis isitadi", "next": "D5_S2", "q": "❓ 5.2: Fenlardagi Ionizatsiya nima?", "kb": ["A: Sochni elektrlanishdan saqlaydi", "B: Tezroq quritadi"], "d": "d5"},
        "D5_S2": {"j": "A: Sochni elektrlanishdan saqlaydi", "next": "FINISH", "q": "🏁 Kurs yakunlandi!", "kb": [], "d": "d5"}
    }

    step = user["step"]
    if step in savollar:
        d_key = savollar[step]["d"]

        # 30 SONIYA TAYMER TEKSHIRUVI
        elapsed = time.time() - user.get("q_start_time", time.time())
        if elapsed > 30:
            user["errors"][d_key] += 1
            user["q_start_time"] = time.time() # Vaqtni yangilash
            save_data(data)
            await message.answer("⏰ Vaqt tugadi! Bu xato deb hisoblandi. Keyingi savolga o'ting!", protect_content=True)

        # JAVOBNI TEKSHIRISH
        if txt == savollar[step]["j"]:
            user["step"] = savollar[step]["next"]
            user["q_start_time"] = time.time()
            
            # KURS TUGAGANDA
            if user["step"] == "FINISH":
                user["last_done_date"] = bugun
                save_data(data)
                
                # ADMINGA HISOBOT YUBORISH
                jami_xato = sum(user["errors"].values())
                report = (
                    f"🔔 **YANGI NATIJA**\n\n"
                    f"👤 **Xodim:** {user['name']}\n"
                    f"📅 **Sana:** {bugun}\n\n"
                    f"❌ **Xatolar (darslar bo'yicha):**\n"
                    f"1-dars: {user['errors']['d1']} ta\n"
                    f"2-dars: {user['errors']['d2']} ta\n"
                    f"3-dars: {user['errors']['d3']} ta\n"
                    f"4-dars: {user['errors']['d4']} ta\n"
                    f"5-dars: {user['errors']['d5']} ta\n\n"
                    f"🏆 **Umumiy xatolar:** {jami_xato} ta"
                )
                
                try:
                    await bot.send_message(ADMIN_ID, report, parse_mode="Markdown")
                except Exception as e:
                    logging.error(f"Adminga xabar yuborishda xato: {e}")

                await message.answer("🏁 Tabriklaymiz! Kursni muvaffaqiyatli tugatdingiz. Natijalariz rahbariyatga yuborildi.", 
                                     reply_markup=ReplyKeyboardRemove())
                return

            save_data(data)
            kb = get_kb(savollar[step]["kb"]) if savollar[step]["kb"] else ReplyKeyboardRemove()
            await message.answer(f"✅ To'g'ri!\n\n{savollar[step]['q']}", reply_markup=kb, protect_content=True)
        else:
            # NOTOG'RI JAVOB
            user["errors"][d_key] += 1
            save_data(data)
            await message.answer("❌ Xato! Yana urinib ko'ring (vaqt ketyapti):", protect_content=True)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':

    asyncio.run(main())
