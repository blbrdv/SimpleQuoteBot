import os
import traceback
from os import getenv

from pyrogram import Client, filters
from pyrogram.types import Message

from image import draw

app = Client("QuoteBot", api_hash=getenv("USER_HASH"), api_id=int(getenv("USER_ID")))
history = {}


@app.on_message(filters.command(["start"]))
async def command_start(_, message: Message) -> None:
    await message.reply(
        "1. Forward messages to private chat with bot.\n"
        "2. Reply '/quote' command on first message.\n"
        "3. ???\n"
        "4. Profit!\n"
    )


@app.on_message(filters.command(["quote"]))
async def command_quote(client, message: Message) -> None:
    if not message.reply_to_message:
        await command_start(client, message)
        return

    # not supposed to happen
    if not history:
        await message.reply("Something went wrong. Try again later.")
        return

    messages = [
        value.text
        for key, value in history[message.chat.id].items()
        if key >= message.reply_to_message_id
    ]

    # not supposed to happen
    if not messages:
        await message.reply("Something went wrong. Try again later.")
        return

    file_name = f"{message.chat.id}.png"

    try:
        draw(messages, file_name)
        await message.reply_photo(file_name)

        os.remove(file_name)
        history[message.chat.id].clear()
    except:
        await message.reply(traceback.format_exc())


@app.on_message()
async def regular_message(_, message: Message) -> None:
    try:
        _ = history[message.chat.id]
    except:
        history[message.chat.id] = {}

    history[message.chat.id][message.id] = message


def main() -> None:
    app.run()
