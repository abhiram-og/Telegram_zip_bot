import threading
import time

from app.sessions import cleanup_sessions

def start_cleanup_worker():

    def worker():

        while True:
            cleanup_sessions()

            time.sleep(600)

    thread = threading.Thread(
        target=worker,
        daemon=True
    )

    thread.start()