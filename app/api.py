from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from app.zip_stream import generate_zip_stream
from app.cleanup import start_cleanup_worker

app = FastAPI()

start_cleanup_worker()


@app.get("/")
def home():

    return {
        "status": "ZIP server running"
    }


@app.get("/download/{session_id}")
def download(session_id: str):

    zip_stream = generate_zip_stream(session_id)

    if not zip_stream:

        return {
            "error": "Session not found"
        }

    return StreamingResponse(
        zip_stream,
        media_type="application/zip",
        headers={
            "Content-Disposition":
            "attachment; filename=files.zip"
        }
    )