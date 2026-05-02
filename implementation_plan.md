# Make telegram_zip_bot Production-Ready

Bring the codebase in line with the user's production README vision: true streaming ZIP for 2GB+ files, low memory, stable architecture.

## Gaps Between README Vision & Current Code

| README Promise | Current Reality |
|---|---|
| "Memory usage remains low" | `zip_stream.py` collects **all chunks into a list** before returning — 2GB file = 2GB+ RAM |
| "Handles large files (2GB+)" | New Pyrogram client per request + in-memory buffering makes this impractical |
| "Production-safe architecture" | Hardcoded secrets, no logging outside bot, no error handling, no `__init__.py` |
| "requirements.txt" listed | File is empty |
| "Never share BOT_TOKEN" | Hardcoded in 2 source files |

---

## Proposed Changes

### 1. Config Module — Extract Secrets

#### [NEW] [config.py](file:///c:/Users/abhir/Desktop/Projects/telegram_zip_bot/app/config.py)

Central config file using environment variables with `python-dotenv`:

```python
import os
from dotenv import load_dotenv
load_dotenv()

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8000")
```

#### [NEW] [.env](file:///c:/Users/abhir/Desktop/Projects/telegram_zip_bot/.env)

```
API_ID=37725631
API_HASH=1d8359471a44311bd343b9cf4a024f98
BOT_TOKEN=8623239572:AAFY0uJPYiIFaMfLG0Unr82PFAzJtUs57zU
BASE_URL=http://127.0.0.1:8000
```

#### [NEW] [.gitignore](file:///c:/Users/abhir/Desktop/Projects/telegram_zip_bot/.gitignore)

Exclude `.env`, `venv/`, `sessions.db`, `__pycache__/`, `*.session*`.

---

### 2. True Streaming ZIP — The Core Fix

#### [MODIFY] [zip_stream.py](file:///c:/Users/abhir/Desktop/Projects/telegram_zip_bot/app/zip_stream.py)

> [!IMPORTANT]
> This is the most critical change. The current approach loads all file bytes into memory, which breaks the 2GB+ promise.

**New approach:**
- Use a **shared, long-lived Pyrogram client** (started once at API startup, not per request).
- Use a **synchronous generator** that yields ZIP chunks incrementally.
- `zipstream` already supports iterators via `write_iter()` — we just need to feed it a proper per-file generator that pulls chunks from Telegram on demand.
- Since FastAPI's `StreamingResponse` consumes a sync iterator in a threadpool, and we need to call async Pyrogram from that thread, we'll use a dedicated event loop running in a background thread to bridge async→sync.

**Architecture:**

```
FastAPI StreamingResponse (sync iterator)
  └── yields from zipstream.ZipFile (sync iterator)
        └── per-file generator calls Pyrogram stream_media (async → bridged to sync)
              └── shared Pyrogram Client (long-lived, started at API boot)
```

---

### 3. Shared Pyrogram Client Lifecycle

#### [MODIFY] [api.py](file:///c:/Users/abhir/Desktop/Projects/telegram_zip_bot/app/api.py)

- Use FastAPI **lifespan** context manager to start/stop the shared Pyrogram client and the cleanup worker.
- Pass the client to `generate_zip_stream()`.
- Add proper HTTP error responses (404 for missing sessions).
- Add logging.

---

### 4. Bot Cleanup

#### [MODIFY] [bot.py](file:///c:/Users/abhir/Desktop/Projects/telegram_zip_bot/app/bot.py)

- Import credentials from `config.py` instead of hardcoding.
- Fix import path: `from sessions import ...` → `from app.sessions import ...` for consistency.
- Since bot.py is run directly (`python app/bot.py`), we'll add `sys.path` handling or use `python -m app.bot`.

---

### 5. Sessions & DB Improvements

#### [MODIFY] [sessions.py](file:///c:/Users/abhir/Desktop/Projects/telegram_zip_bot/app/sessions.py)

- Add index on `created_at` for faster cleanup queries.
- Add index on `session_id` for faster lookups.
- Use context managers for DB connections.
- Import DB path from config (relative to project root).

---

### 6. Cleanup Worker

#### [MODIFY] [cleanup.py](file:///c:/Users/abhir/Desktop/Projects/telegram_zip_bot/app/cleanup.py)

- Add logging so you can see when cleanups happen.
- No longer called at module import time (moved to lifespan).

---

### 7. Package & Dependencies

#### [NEW] [\_\_init\_\_.py](file:///c:/Users/abhir/Desktop/Projects/telegram_zip_bot/app/__init__.py)

Empty file to make `app/` a proper Python package.

#### [MODIFY] [requirements.txt](file:///c:/Users/abhir/Desktop/Projects/telegram_zip_bot/requirements.txt)

```
pyrogram
tgcrypto
fastapi
uvicorn
zipstream-new
python-dotenv
```

---

## Open Questions

> [!IMPORTANT]
> **Running the bot:** Currently `bot.py` is run as `python app/bot.py` which means it can't use `from app.sessions import ...` without path hacks. Two options:
> 1. Run as `python -m app.bot` from the project root (cleanest)
> 2. Add `sys.path` manipulation in `bot.py`
> 
> I'll go with option 1 and update the instructions. Is that okay?

> [!IMPORTANT]
> **Your bot token is exposed in this conversation and in Git history.** After these changes, I strongly recommend regenerating it via BotFather (`/revoke`).

---

## Verification Plan

### Automated Tests
1. Start the API server: `uvicorn app.api:app --host 0.0.0.0 --port 8000`
2. Start the bot: `python -m app.bot`
3. Verify the health endpoint returns `{"status": "ZIP server running"}`
4. Hit a non-existent session → confirm 404 response
5. Forward files to the bot, send `/done`, and download the ZIP

### Manual Verification
- Monitor RAM usage during a large file download to confirm streaming works
- Check logs for Pyrogram client lifecycle events
