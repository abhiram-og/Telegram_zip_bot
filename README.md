# Telegram ZIP Bot

A Telegram bot that lets users forward multiple files and download them all as a single ZIP archive via a generated link.

## How It Works

1. **Send files** — Forward or send documents to the bot on Telegram
2. **Get a link** — Send `/done` and the bot returns a download URL
3. **Download** — Open the link to download all your files bundled into one `.zip`

## Tech Stack

- **[Pyrogram](https://docs.pyrogram.org/)** — Telegram Bot API client
- **[FastAPI](https://fastapi.tiangolo.com/)** — HTTP server for serving ZIP downloads
- **[zipstream-new](https://pypi.org/project/zipstream-new/)** — Streaming ZIP generation
- **SQLite** — Lightweight session/file metadata storage
- **Uvicorn** — ASGI server

## Project Structure

```
telegram_zip_bot/
├── app/
│   ├── bot.py           # Telegram bot (handles /start, file forwarding, /done)
│   ├── api.py           # FastAPI server (serves /download/<session_id>)
│   ├── zip_stream.py    # Downloads files from Telegram & streams as ZIP
│   ├── sessions.py      # SQLite session & file metadata management
│   └── cleanup.py       # Background worker to purge expired sessions (24h)
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup

### Prerequisites

- Python 3.11+
- A Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Telegram API credentials (from [my.telegram.org](https://my.telegram.org))

### Installation

```bash
# Clone the repo
git clone https://github.com/abhiram-og/Telegram_zip_bot.git
cd Telegram_zip_bot

# Create a virtual environment
python -m venv venv

# Activate it
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Update the following values in `app/bot.py` and `app/zip_stream.py`:

```python
API_ID = your_api_id
API_HASH = "your_api_hash"
BOT_TOKEN = "your_bot_token"
```

> **Tip:** Move these to environment variables or a `.env` file to keep them out of source control.

### Running

You need to run **two processes** — the bot and the API server:

```bash
# Terminal 1 — Start the FastAPI server
uvicorn app.api:app --host 0.0.0.0 --port 8000

# Terminal 2 — Start the Telegram bot
python -m app.bot
```

## Bot Commands

| Command  | Description                              |
|----------|------------------------------------------|
| `/start` | Welcome message with usage instructions  |
| `/done`  | Generates a ZIP download link            |

## API Endpoints

| Method | Endpoint                  | Description                    |
|--------|---------------------------|--------------------------------|
| GET    | `/`                       | Health check                   |
| GET    | `/download/{session_id}`  | Download session files as ZIP  |

## License

This project is open source and available under the [MIT License](LICENSE).
