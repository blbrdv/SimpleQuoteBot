import asyncio
import logging
import os
import traceback
import sys
from datetime import timezone
from os import getenv

from aiogram import Dispatcher, Bot, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import BotCommand, Message, InputFile, FSInputFile

from image import draw

dispatcher = Dispatcher()
history = {}


@dispatcher.message(CommandStart())
async def _on_start(message: Message) -> None:
    await message.reply(
        "1. Forward messages to private chat with bot.\n"
        "2. Reply '/quote' command on first message.\n"
        "3. ???\n"
        "4. Profit!\n"
    )


@dispatcher.message(Command(BotCommand(command="quote", description="Create quote")))
async def _on_quote(message: Message) -> None:
    reply = message.reply_to_message  # storing it b/c aiogram is retarded
    if not reply:
        await _on_start(message)
        return

    # not supposed to happen
    if not history:
        await _on_start(message)
        return

    messages = []
    for key, message in history[message.chat.id].items():
        if key >= reply.message_id:
            time = message.date.replace(tzinfo=timezone.utc).strftime("%H:%M")
            messages.append((message.md_text, time))

    # not supposed to happen
    if not messages:
        await message.reply("Something went wrong. Try again later.")
        return

    file_name = f"{message.chat.id}.png"

    try:
        draw(messages, file_name)
        await message.reply_photo(FSInputFile(file_name))

        os.remove(file_name)
        history[message.chat.id].clear()
    except:
        if getenv("DEBUG"):
            await message.reply(traceback.format_exc())
        else:
            print(traceback.format_exc(), file=sys.stderr)


@dispatcher.message()
async def _on_message(message: types.Message) -> None:
    try:
        _ = history[message.chat.id]
    except:
        history[message.chat.id] = {}

    # temporary hack for saving memory
    # TODO: remove when better hosting
    if len(history[message.chat.id]) >= 50:
        await message.reply("Too big request. Try to split your messages.")
        history[message.chat.id] = {}
    else:
        history[message.chat.id][message.message_id] = message


async def _start_bot() -> None:
    bot = Bot(getenv("BOT_TOKEN"), parse_mode=ParseMode.MARKDOWN)

    print('(Press Ctrl+C to stop this)')
    await dispatcher.start_polling(bot)


def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(_start_bot())
