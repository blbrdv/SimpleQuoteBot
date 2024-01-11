from os import getenv

from pyrogram import Client, filters

app = Client("QuoteBot", bot_token=getenv("BOT_TOKEN"), api_hash=getenv("USER_HASH"), api_id=int(getenv("USER_ID")))


@app.on_message(filters.command(["start"]))
async def command_start(_, message) -> None:
    await message.reply("1. Forward messages to private chat with bot.\n"
                        "2. Reply '/quote' command on first message.\n"
                        "3. ???\n"
                        "4. Profit!\n")


@app.on_message(filters.command(["quote"]))
async def command_quote(client, message) -> None:
    if not message.reply_to_message:
        await command_start(client, message)
        return

    await message.reply('/quote')


def main() -> None:
    app.run()
