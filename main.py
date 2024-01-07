import logging
import sys
from os import getenv

from aiohttp import web

from aiogram import Bot, Dispatcher, Router
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

TOKEN = getenv("BOT_TOKEN")
WEB_SERVER_HOST = getenv("WEBHOOK_URL")
WEB_SERVER_PORT = 8080
WEBHOOK_PATH = "/webhook"
WEBHOOK_SECRET = getenv("WEBHOOK_SECRET")
BASE_WEBHOOK_URL = getenv("WEBHOOK_URL")

router = Router()


async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}", secret_token=WEBHOOK_SECRET)


def main() -> None:
    dispatcher = Dispatcher()
    dispatcher.include_router(router)
    dispatcher.startup.register(on_startup)

    bot = Bot(TOKEN, parse_mode=ParseMode.MARKDOWN_V2)
    app = web.Application()

    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dispatcher,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)

    setup_application(app, dispatcher, bot=bot)
    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
