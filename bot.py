import logging
from aiogram import Bot, Dispatcher, executor, types

# ======= TOKEN va sozlamalar =======
TOKEN = "7953124737:AAFdL93rmF5l69b2xCxL0y7FsET2D0Kzn8c"  # <-- BotFather'dan olingan tokenni shu yerga yoz
CHANNELS = ["@animitsu", "@animitsu_official"]  # <-- obuna tekshiriladigan kanal username'lari

# ======= Anime mapping =======
# Param → file_id (video)
ANIME_DATABASE = {
    "dandadan2f_1": "BAACAgIAAxkBAANkaHI1dSeH6c5hGIqB8f83sX9jUGsAAo9zAAKz-5FLwWKgv2KD5B42BA",
    "dandadan2f_2": "BAACAgIAAxkBAANlaHI1y90YQGHvr5la91677qjr7mQAAp1zAAKz-5FLIm0SitKxiq82BA",
    # bu yerga xohlagancha qo'sh
}

# ======= Logging =======
logging.basicConfig(level=logging.INFO)

# ======= Bot va Dispatcher =======
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# ======= Obuna tekshiruvchi funksiya =======
async def check_subscriptions(user_id):
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(channel, user_id)
            if member.status in ("left", "kicked"):
                return False
        except:
            return False
    return True

# ======= /start handler =======
@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    args = message.get_args()
    subscribed = await check_subscriptions(user_id)

    if not subscribed:
        markup = types.InlineKeyboardMarkup(row_width=1)
        for ch in CHANNELS:
            markup.add(types.InlineKeyboardButton("✅ Obuna bo'lish", url=f"https://t.me/{ch[1:]}"))
        markup.add(types.InlineKeyboardButton("🔄 Tekshirish", callback_data=f"retry:{args}"))
        await message.answer(
            "❗️Iltimos, quyidagi kanallarga obuna bo‘ling va tekshirish tugmasini bosing:",
            reply_markup=markup
        )
        return

    if args:
        if args in ANIME_DATABASE:
            await message.answer_chat_action('upload_video')
            await message.answer_video(ANIME_DATABASE[args], caption=f"✅ Mana so'ralgan anime!")
        else:
            await message.answer("⚠️ Kechirasiz, bunday anime topilmadi.")
    else:
        await message.answer("👋 Salom! animitsu botiga xush kelibsiz.")

# ======= Callback handler (Tekshirish) =======
@dp.callback_query_handler(lambda c: c.data and c.data.startswith("retry:"))
async def retry_callback(call: types.CallbackQuery):
    await call.answer()  # Loading tugmasini yopish
    user_id = call.from_user.id
    args = call.data.split(":", 1)[1]
    subscribed = await check_subscriptions(user_id)

    if subscribed:
        if args in ANIME_DATABASE:
            await call.message.answer_chat_action('upload_video')
            await call.message.answer_video(ANIME_DATABASE[args], caption="✅ Mana so'ralgan anime!")
        else:
            await call.message.answer("✅ Obuna bo'ldingiz, ammo bu anime topilmadi.")
    else:
        await call.message.answer("❗️Hali ham obuna emassiz.")

# ======= Admin uchun - file_id chiqaruvchi handler =======
@dp.message_handler(content_types=['video', 'photo', 'document'])
async def get_file_id_handler(message: types.Message):
    text = "❗️File ID topilmadi."
    if message.video:
        text = f"📌 Video file_id:\n{message.video.file_id}"
    elif message.photo:
        text = f"📌 Photo file_id:\n{message.photo[-1].file_id}"
    elif message.document:
        text = f"📌 Document file_id:\n{message.document.file_id}"

    await message.answer(text)

# ======= Botni ishga tushurish =======
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
