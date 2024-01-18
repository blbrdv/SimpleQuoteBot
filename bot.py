import asyncio
import logging
import os
import traceback
import sys
from os import getenv

from aiogram import Dispatcher, Bot, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import BotCommand, Message, FSInputFile
from Message import Message as Msg
from Speech import Speech

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
async def _on_quote(incoming_message: Message) -> None:
    reply = incoming_message.reply_to_message  # storing it b/c aiogram is retarded
    if not reply:
        await _on_start(incoming_message)
        return

    # not supposed to happen
    if not history:
        await _on_start(incoming_message)
        return

    data = []
    last_user_id = 0
    for key, message in history[incoming_message.chat.id].items():
        if key < reply.message_id:
            continue

        user_id = 0
        user_name = ""
        if message.forward_from:
            user_id = message.forward_origin.sender_user.id
            user_name = message.forward_origin.sender_user.full_name
        else:
            user_id = message.from_user.id
            user_name = message.from_user.full_name

        if last_user_id == user_id:
            data[-1].messages.append(Msg(message.md_text, message.date))
        else:
            data.append(
                Speech(
                    user_name,
                    "",
                    [Msg(message.md_text, message.date)],
                )
            )

        last_user_id = user_id

    messages_empty = False
    for speech in data:
        if not speech.messages:
            messages_empty = True
            break

    # not supposed to happen
    if not data or messages_empty:
        await incoming_message.reply("Something went wrong. Try again later.")
        return

    file_name = f"{incoming_message.chat.id}.png"

    try:
        draw(data, file_name)
        await incoming_message.reply_photo(FSInputFile(file_name))

        os.remove(file_name)
        history[incoming_message.chat.id].clear()
    except:
        if getenv("DEBUG"):
            await incoming_message.reply(traceback.format_exc())
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

    print("(Press Ctrl+C to stop this)")
    await dispatcher.start_polling(bot)


def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(_start_bot())
