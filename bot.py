import asyncio
import os
import traceback
import sys
import xxhash
from datetime import datetime
from os import getenv

from aiogram import Dispatcher, Bot, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import BotCommand, Message, FSInputFile
from aiogram.filters.command import Command
from aiogram.enums.message_origin_type import MessageOriginType

from Author import Author
from Message import Message as Msg
from Speech import Speech

from image import draw

dispatcher = Dispatcher()
bot = Bot(getenv("BOT_TOKEN"), parse_mode=ParseMode.MARKDOWN)
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
        firstname = ""
        lastname = ""
        message_datetime = datetime.now()
        pfp: str | None = None
        if message.forward_origin:
            if message.forward_origin.type == MessageOriginType.HIDDEN_USER:
                # hidden user doesn't provide id :^(
                user_id = xxhash.xxh32_intdigest(
                    message.forward_origin.sender_user_name
                )
                name = message.forward_origin.sender_user_name.split()
                firstname = name[0]
                lastname = " ".join(name[1:])
            else:
                user_id = message.forward_origin.sender_user.id
                firstname = message.forward_origin.sender_user.first_name
                lastname = message.forward_origin.sender_user.last_name

                pfps = await bot.get_user_profile_photos(user_id)
                if pfps.total_count > 0:
                    pfp = pfps.photos[0][0].file_id
                else:
                    pfp = None

            message_datetime = message.forward_origin.date
        else:
            user_id = message.from_user.id
            firstname = message.from_user.first_name
            lastname = message.from_user.last_name
            message_datetime = message.date

        if last_user_id == user_id:
            data[-1].messages.append(Msg(message.md_text, message_datetime))
        else:
            if len(data) > 0 and data[-1]:
                data[-1].messages[-1].last = True

            author = Author(user_id, firstname, lastname)
            data.append(
                Speech(
                    author,
                    pfp,
                    [Msg(message.md_text, message_datetime, header=author.full_name)],
                )
            )

        last_user_id = user_id

    data[-1].messages[-1].last = True

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
    print("(Press Ctrl+C to stop this)")
    await dispatcher.start_polling(bot)


def main() -> None:
    asyncio.run(_start_bot())
