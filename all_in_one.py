import re
import queue
import threading
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
import speech_recognition as sr
import pyttsx3

UFW_PATH = "/usr/sbin/ufw"  # adjust if ufw is elsewhere
MAX_WORKER_QUEUE = 32
COMMAND_TIMEOUT = 10  # seconds to wait for ufw command to finish
RATE_LIMIT_SECONDS = 1.0  # minimum seconds between accepted commands
ALLOWED_COMMANDS = {
    "enable": [ "sudo", UFW_PATH, "enable" ],
    "disable": [ "sudo", UFW_PATH, "disable" ],
    "status": [ "sudo", UFW_PATH, "status", "verbose" ],
}

PORT_RE = re.compile(r"\b([0-9]{1,5})\b")
VALID_PORT_RANGE = (1, 65535)

command_queue = queue.Queue(maxsize=MAX_WORKER_QUEUE)
tts_queue = queue.Queue()
_last_command_time = 0.0
_last_command_lock = threading.Lock()

tts_engine = pyttsx3.init()
tts_lock = threading.Lock()

def tts_worker():
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

def speak(text):
    print("TTS:", text)
    try:
        tts_queue.put_nowait(text)
    except queue.Full:
        pass

def ufw_worker():
    while True:
        item = command_queue.get()
        if item is None:
            break
        cmd_args, human_text = item
        print("Executing:", cmd_args)
        try:
            proc = subprocess.Popen(cmd_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            try:
                stdout, stderr = proc.communicate(timeout=COMMAND_TIMEOUT)
            except subprocess.TimeoutExpired:
                proc.kill()
                stdout, stderr = proc.communicate()
                speak("Command timed out")
                print("Timeout:", cmd_args)
                command_queue.task_done()
                continue

            if proc.returncode == 0:
                if "status" in cmd_args:
                    speak("Firewall status: " + (stdout.strip() or "no output"))
                else:
                    speak(human_text + " — done")
                print("UFW stdout:", stdout)
            else:
                speak("Error executing firewall command")
                print("UFW stderr:", stderr.strip())
        except Exception as e:
            print("Execution error:", e)
            speak("Internal error while executing command")
        finally:
            command_queue.task_done()

ufw_thread = threading.Thread(target=ufw_worker, daemon=True)
ufw_thread.start()

def rate_limited():
    global _last_command_time
    with _last_command_lock:
        now = time.time()
        if now - _last_command_time < RATE_LIMIT_SECONDS:
            return True
        _last_command_time = now
        return False

def enqueue_command(cmd_key_or_args, human_text):
    
    if rate_limited():
        speak("Command ignored: too fast")
        return

    if isinstance(cmd_key_or_args, str):
        args = ALLOWED_COMMANDS.get(cmd_key_or_args)
        if not args:
            speak("Unknown command")
            return
    else:
        args = cmd_key_or_args

    try:
        command_queue.put_nowait((args, human_text))
    except queue.Full:
        speak("Command queue is full, try again later")

def parse_and_handle(command_text):
    
    text = command_text.lower().strip()
    print("Heard:", text)

    if "enable firewall" in text or text == "enable firewall" or text == "enable":
        enqueue_command("enable", "Firewall enabled")
        return

    if "disable firewall" in text or text == "disable firewall" or text == "disable":
        enqueue_command("disable", "Firewall disabled")
        return

    if "status" == text or "firewall status" in text or "status" in text:
        enqueue_command("status", "Showing firewall status")
        return

    if "block port" in text or text.startswith("block "):
        m = PORT_RE.search(text)
        if not m:
            speak("Please specify a numeric port to block")
            return
        port = int(m.group(1))
        if PORT_RE and (VALID_PORT_RANGE[0] <= port <= VALID_PORT_RANGE[1]):
            args = ["sudo", UFW_PATH, "deny", str(port)]
            enqueue_command(args, f"Blocked port {port}")
            return
        else:
            speak("Port out of range")
            return

    if "allow port" in text or text.startswith("allow "):
        m = PORT_RE.search(text)
        if not m:
            speak("Please specify a numeric port to allow")
            return
        port = int(m.group(1))
        if VALID_PORT_RANGE[0] <= port <= VALID_PORT_RANGE[1]:
            args = ["sudo", UFW_PATH, "allow", str(port)]
            enqueue_command(args, f"Allowed port {port}")
            return
        else:
            speak("Port out of range")
            return

    speak("Command not recognized")

recognizer = sr.Recognizer()
mic = sr.Microphone()

executor = ThreadPoolExecutor(max_workers=4)

def background_callback(recognizer_obj, audio):
    
    executor.submit(process_audio, recognizer_obj, audio)

def process_audio(recognizer_obj, audio):
    try:
        text = recognizer_obj.recognize_google(audio)
        parse_and_handle(text)
    except sr.UnknownValueError:
        pass
    except sr.RequestError as e:
        print("Speech API error:", e)
        speak("Speech recognition service error")

def main():
    speak("Voice Firewall Control Activated")
    print("Calibrating for ambient noise, please be quiet...")
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=1.0)
    stop_listening = recognizer.listen_in_background(mic, background_callback)
    print("Listening in background. Say 'enable firewall', 'disable firewall', 'status', 'block port 22', or 'allow port 80'.")
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        stop_listening(wait_for_stop=False)
        command_queue.put(None)
        tts_queue.put(None)
        executor.shutdown(wait=False)
        time.sleep(0.5)

if __name__ == "__main__":
    main()

