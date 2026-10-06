import logging
import uuid
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

BOT_TOKEN = "8572741655:AAGnFIPw1ewjXcB0Koz-QwrLEfBS38i4yJw"
ADMIN_CHAT_ID = 5303673207
SITE_DOMAIN = "https://magenta-julienne-22.tiiny.site"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

tokens_db = {}

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    if message.chat.id != ADMIN_CHAT_ID:
        return
    await message.answer(
        "👋 *Бот управления одноразовыми ссылками калькулятора*\n\n"
        "Отправьте имя или название компании клиента, чтобы создать защищённую одноразовую ссылку.\n\n"
        "Пример: ТОО Агро-Инвест",
        parse_mode="Markdown"
    )

@dp.message()
async def generate_link(message: types.Message):
    if message.chat.id != ADMIN_CHAT_ID:
        return

    client_name = message.text.strip()
    token = str(uuid.uuid4())[:8]

    tokens_db[token] = {
        "client": client_name,
        "status": "active"
    }

    client_link = f"{SITE_DOMAIN}/?token={token}"

    await message.answer(
        f"✅ *Одноразовая ссылка создана!*\n\n"
        f"👤 Клиент: *{client_name}*\n"
        f"🔗 Ссылка: {client_link}\n\n"
        f"Скопируйте ссылку и отправьте в WhatsApp.",
        parse_mode="Markdown"
    )

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if _name_ == "_main_":
    asyncio.run(main())
