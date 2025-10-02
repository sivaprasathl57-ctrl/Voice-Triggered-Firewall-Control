import queue
import threading
import pyttsx3

tts_queue = queue.Queue()
tts_engine = pyttsx3.init()
tts_lock = threading.Lock()

def tts_worker():
    """Background worker for speaking queued text."""
    while True:
        text = tts_queue.get()
        if text is None:
            break
        try:
            with tts_lock:
                tts_engine.say(text)
                tts_engine.runAndWait()
        except Exception as e:
            print("TTS error:", e)
        tts_queue.task_done()

tts_thread = threading.Thread(target=tts_worker, daemon=True)
tts_thread.start()

def speak(text: str):
    """Queue text for TTS and print it."""
    print("TTS:", text)
    try:
        tts_queue.put_nowait(text)
    except queue.Full:
        pass


