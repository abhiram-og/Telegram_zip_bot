import asyncio
import zipstream

from pyrogram import Client

from app.sessions import get_files

API_ID = 37725631
API_HASH = "1d8359471a44311bd343b9cf4a024f98"
BOT_TOKEN = "8623239572:AAFY0uJPYiIFaMfLG0Unr82PFAzJtUs57zU"


def generate_zip_stream(session_id):
    """
    Runs a Pyrogram client in a brand-new event loop (required because
    FastAPI calls this from an AnyIO worker thread that has no event loop),
    downloads all files for the session, and yields zip chunks.
    """

    files = get_files(session_id)

    if not files:
        raise Exception("No files in session")

    # Create a dedicated event loop for this thread.
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def _stream():
        async with Client(
            "zip_stream_client",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            in_memory=True,
        ) as client:
            z = zipstream.ZipFile(
                mode="w",
                compression=zipstream.ZIP_DEFLATED,
            )

            for file in files:
                file_id = file["file_id"]
                filename = file["name"]

                # Capture file_id in closure to avoid late-binding bug.
                def make_generator(fid):
                    async def _gen():
                        async for chunk in client.stream_media(fid):
                            yield chunk
                    return _gen

                z.write_iter(filename, make_generator(file_id)())

            # Consume the zipstream and yield bytes.
            for chunk in z:
                yield chunk

    # Run the async generator synchronously and yield chunks to FastAPI.
    async def _collect():
        chunks = []
        async for chunk in _stream():
            chunks.append(chunk)
        return chunks

    chunks = loop.run_until_complete(_collect())
    loop.close()

    return iter(chunks)