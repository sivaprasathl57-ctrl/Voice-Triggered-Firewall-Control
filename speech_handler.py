import speech_recognition as sr
from concurrent.futures import ThreadPoolExecutor
from firewall import enqueue_command
from utils import extract_port, rate_limited
from tts_engine import speak

UFW_PATH = "/usr/sbin/ufw"
ALLOWED_COMMANDS = {
    "enable": ["sudo", UFW_PATH, "enable"],
    "disable": ["sudo", UFW_PATH, "disable"],
    "status": ["sudo", UFW_PATH, "status", "verbose"],
}

executor = ThreadPoolExecutor(max_workers=4)
recognizer = sr.Recognizer()
mic = sr.Microphone()

def parse_and_handle(command_text: str):
    text = command_text.lower().strip()
    print("Heard:", text)

    if rate_limited():
        speak("Command ignored: too fast")
        return

    if "enable firewall" in text or text == "enable":
        enqueue_command(ALLOWED_COMMANDS["enable"], "Firewall enabled")
    elif "disable firewall" in text or text == "disable":
        enqueue_command(ALLOWED_COMMANDS["disable"], "Firewall disabled")
    elif "status" in text:
        enqueue_command(ALLOWED_COMMANDS["status"], "Showing firewall status")
    elif "block port" in text:
        port = extract_port(text)
        if port:
            enqueue_command(["sudo", UFW_PATH, "deny", str(port)], f"Blocked port {port}")
        else:
            speak("Please specify a valid port to block")
    elif "allow port" in text:
        port = extract_port(text)
        if port:
            enqueue_command(["sudo", UFW_PATH, "allow", str(port)], f"Allowed port {port}")
        else:
            speak("Please specify a valid port to allow")
    else:
        speak("Command not recognized")

def process_audio(recognizer_obj, audio):
    try:
        text = recognizer_obj.recognize_google(audio)
        parse_and_handle(text)
    except sr.UnknownValueError:
        pass
    except sr.RequestError as e:
        print("Speech API error:", e)
        speak("Speech recognition service error")

def background_callback(recognizer_obj, audio):
    executor.submit(process_audio, recognizer_obj, audio)
