import logging
import os

from dotenv import load_dotenv
from pyrogram import Client, filters

from sessions import (
    create_session,
    add_file
)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

LOGGER = logging.getLogger(__name__)

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8000")

app = Client(
    "zip_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

user_sessions = {}


@app.on_message(filters.command("start"))
async def start_handler(client, message):

    await message.reply_text(
        "Forward files to me.\n"
        "When finished, send /done."
    )


@app.on_message(filters.document)
async def file_handler(client, message):

    user_id = message.from_user.id

    if user_id not in user_sessions:

        session_id = create_session()

        user_sessions[user_id] = session_id

        LOGGER.info(
            f"New session created: {session_id}"
        )

    session_id = user_sessions[user_id]

    document = message.document

    file_id = document.file_id
    name = document.file_name
    size = document.file_size

    add_file(
        session_id,
        file_id,
        name,
        size
    )

    await message.reply_text(
        f"Added:\n{name}"
    )


@app.on_message(filters.command("done"))
async def done_handler(client, message):

    user_id = message.from_user.id

    if user_id not in user_sessions:

        await message.reply_text(
            "No files received."
        )

        return

    session_id = user_sessions[user_id]

    link = f"{BASE_URL}/download/{session_id}"

    await message.reply_text(
        f"Download link:\n{link}"
    )

    del user_sessions[user_id]


if __name__ == "__main__":

    LOGGER.info("Bot started")

    app.run()