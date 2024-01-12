from os import getenv

from pyrogram import Client, filters
from pyrogram.types import Message

app = Client("QuoteBot", api_hash=getenv("USER_HASH"), api_id=int(getenv("USER_ID")))
history = {}


@app.on_message(filters.command(["start"]))
async def command_start(_, message: Message) -> None:
    await message.reply("1. Forward messages to private chat with bot.\n"
                        "2. Reply '/quote' command on first message.\n"
                        "3. ???\n"
                        "4. Profit!\n")


@app.on_message(filters.command(["quote"]))
async def command_quote(client, message: Message) -> None:
    if not message.reply_to_message:
        await command_start(client, message)
        return

    messages = [v for k, v in history[message.chat.id].items() if k >= message.reply_to_message_id]

    if not messages:
        await message.reply("Something went wrong. Try again later.")
        return

    for msg in messages:
        print(msg)

    history[message.chat.id].clear()


@app.on_message()
async def regular_message(_, message: Message) -> None:
    try:
        _ = history[message.chat.id]
    except:
        history[message.chat.id] = {}

    history[message.chat.id][message.id] = message.text


def main() -> None:
    app.run()
