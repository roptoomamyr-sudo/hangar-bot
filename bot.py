import logging
import uuid
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiohttp import web

BOT_TOKEN = "8572741655:AAGnFIPw1ewjXcB0Koz-QwrLEfBS38i4yJw"
ADMIN_CHAT_ID = 5303673207
SITE_DOMAIN = "https://roptoomamyr-sudo.github.io/hangar-bot"

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

async def check_token_handler(request):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    }

    if request.method == "OPTIONS":
        return web.Response(status=200, headers=headers)
    
    token = request.query.get("token")
    user_agent = request.headers.get("User-Agent", "").lower()

    is_bot = any(b in user_agent for b in ["whatsapp", "telegram", "facebookexternalhit", "twitterbot", "meta-externalagent"])
    if is_bot:
        return web.json_response({"status": "preview_ignored"}, headers=headers)

    if token in tokens_db:
        data = tokens_db[token]
        if data["status"] == "active":
            data["status"] = "used"
            await bot.send_message(
                ADMIN_CHAT_ID, 
                f"🔔 *Клиент только что открыл калькулятор!\n\n👤 Клиент: *{data['client']}**",
                parse_mode="Markdown"
            )
            return web.json_response({"status": "valid", "client": data["client"]}, headers=headers)
        else:
            return web.json_response({"status": "used"}, headers=headers)
    
    return web.json_response({"status": "invalid"}, headers=headers)

async def health_check(request):
    return web.Response(text="OK")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    
    app = web.Application()
    app.router.add_get("/", health_check)
    app.router.add_get("/api/check-token", check_token_handler)
    app.router.add_options("/api/check-token", check_token_handler)
    
    port = int(os.environ.get("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
