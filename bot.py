import os
import traceback
import sys
from datetime import datetime
from os import getenv

from pyrogram import Client, filters
from pyrogram.types import Message

from image import draw

app = Client("QuoteBot", bot_token=getenv("BOT_TOKEN"))
history = {}


@app.on_message(filters.command(["start"]))
async def _on_start(_, message: Message) -> None:
    await message.reply(
        "1. Forward messages to private chat with bot.\n"
        "2. Reply '/quote' command on first message.\n"
        "3. ???\n"
        "4. Profit!\n"
    )


@app.on_message(filters.command(["quote"]))
async def _on_quote(client, message: Message) -> None:
    if not message.reply_to_message:
        await _on_start(client, message)
        return

    # not supposed to happen
    if not history:
        await _on_start(client, message)
        return

    messages = []
    for key, (text, date) in history[message.chat.id].items():
        if key >= message.reply_to_message_id:
            time = date.astimezone(datetime.UTC).strftime("%H:%M")
            messages.append((text, time))

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
        if getenv("DEBUG"):
            await message.reply(traceback.format_exc())
        else:
            print(traceback.format_exc(), file=sys.stderr)


@app.on_message()
async def _on_message(_, message: Message) -> None:
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
        history[message.chat.id][message.id] = message


def main() -> None:
    app.run()
