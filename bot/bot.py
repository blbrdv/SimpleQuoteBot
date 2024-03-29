import asyncio
import os
import shutil
import traceback
import sys
from os import getenv
from typing import Optional

from aiogram import Dispatcher, Bot, types
from aiogram.enums import ParseMode, ContentType
from aiogram.filters import CommandStart
from aiogram.types import BotCommand, Message, FSInputFile
from aiogram.filters.command import Command

from bot.message import Bubble
from bot.logger import Logger
from bot.message import IncomingMessage, Sticker
from bot.params import Theme, Params
from bot.speech import Speech

from bot.draw import draw
from bot.utils import full_path

dispatcher = Dispatcher()
tgbot = Bot(getenv("BOT_TOKEN"), parse_mode=ParseMode.MARKDOWN)
logger = Logger("bot")
history = {}
chrome_executable: Optional[str] = None


@dispatcher.message(CommandStart())
async def _on_start(message: Message) -> None:
    await message.reply(
        "1. Forward messages to private chat with bot.\n"
        "2. Reply `/q <params>` command on first message.\n"
        "3. ???\n"
        "4. Profit!\n"
        "\n"
        "Params:\n"
        " - `dark` - dark theme;\n"
        " - `anon` - hide avatars and names."
    )
    logger.debug(f"Start replayed to {message.from_user.full_name}")


@dispatcher.message(Command(BotCommand(command="q", description="Create quote")))
async def _on_quote(q_message: Message) -> None:
    reply = q_message.reply_to_message  # storing it b/c aiogram is retarded
    if not reply:
        await _on_start(q_message)
        return

    # not supposed to happen
    if not history:
        await _on_start(q_message)
        return

    params_raw = q_message.text.split(" ")[1:]
    theme: Theme = Theme.LIGHT
    if "dark" in params_raw:
        theme = Theme.DARK
    is_anon = "anon" in params_raw
    params = Params(theme, is_anon)

    speeches: list[Speech] = []
    messages: list[IncomingMessage] = []
    last_user_id = 0
    media_group_id: Optional[int] = None
    for key, message in history[q_message.chat.id].items():
        if key < reply.message_id:
            continue

        if message.media_group_id:
            if media_group_id == message.media_group_id:
                messages[-1].media_group_count += 1
                continue
            else:
                media_group_id = message.media_group_id
        else:
            media_group_id = None

        if message.content_type == ContentType.STICKER:
            incoming_message = await Sticker.create(message)
        else:
            incoming_message = await Bubble.create(message)

        if message.reply_to_message:
            for msg in messages:
                if msg.message_id == message.reply_to_message.message_id:
                    incoming_message.reply = msg

        messages.append(incoming_message)

        if last_user_id == incoming_message.author_id:
            speeches[-1].messages.append(incoming_message)
        else:
            speeches.append(Speech([incoming_message]))

        last_user_id = incoming_message.author_id

    messages_empty = False
    for speech in speeches:
        if not speech.messages:
            messages_empty = True
            break

    # not supposed to happen
    if not speeches or messages_empty:
        await q_message.reply("Something went wrong. Try again later.")
        return

    file_name = f"{q_message.chat.id}.png"

    try:
        draw(speeches, chrome_executable, file_name, params)
        logger.debug(f"Picture {file_name} drawn")
        await q_message.reply_photo(FSInputFile(file_name))
        logger.debug(f"Picture {file_name} send")
    except:
        if getenv("DEBUG"):
            await q_message.reply(traceback.format_exc())
        else:
            print(traceback.format_exc(), file=sys.stderr)
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)

        if os.path.exists(full_path("temp")):
            shutil.rmtree(full_path("temp"))

        history[q_message.chat.id].clear()


@dispatcher.message()
async def _on_message(message: types.Message) -> None:
    try:
        _ = history[message.chat.id]
    except:
        history[message.chat.id] = {}

    history[message.chat.id][message.message_id] = message
    logger.debug(f"Message {message.message_id} saved")


async def _start_bot() -> None:
    logger.info("Bot started (Press Ctrl+C to stop it)")
    await dispatcher.start_polling(tgbot)


def main() -> None:
    global chrome_executable
    if len(sys.argv) > 1:
        chrome_executable = sys.argv[1]
    asyncio.run(_start_bot())
