import subprocess
import queue
import threading
from tts_engine import speak

UFW_PATH = "/usr/sbin/ufw"
COMMAND_TIMEOUT = 10
command_queue = queue.Queue()

def ufw_worker():
    while True:
        item = command_queue.get()
        if item is None:
            break
        cmd_args, human_text = item
        print("Executing:", cmd_args)
        try:
            proc = subprocess.Popen(cmd_args, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, text=True)
            stdout, stderr = proc.communicate(timeout=COMMAND_TIMEOUT)

            if proc.returncode == 0:
                if "status" in cmd_args:
                    speak("Firewall status: " + (stdout.strip() or "no output"))
                else:
                    speak(human_text + " — done")
                print("UFW stdout:", stdout)
            else:
                speak("Error executing firewall command")
                print("UFW stderr:", stderr.strip())
        except subprocess.TimeoutExpired:
            speak("Command timed out")
        except Exception as e:
            print("Execution error:", e)
            speak("Internal error while executing command")
        finally:
            command_queue.task_done()

ufw_thread = threading.Thread(target=ufw_worker, daemon=True)
ufw_thread.start()

def enqueue_command(cmd_args, human_text):
    try:
        command_queue.put_nowait((cmd_args, human_text))
    except queue.Full:
        speak("Command queue is full, try again later")
