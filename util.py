import re
import time
import threading

RATE_LIMIT_SECONDS = 1.0
_last_command_time = 0.0
_last_command_lock = threading.Lock()

PORT_RE = re.compile(r"\b([0-9]{1,5})\b")
VALID_PORT_RANGE = (1, 65535)

def extract_port(text: str):
    """Extract port number from text if valid."""
    m = PORT_RE.search(text)
    if not m:
        return None
    port = int(m.group(1))
    if VALID_PORT_RANGE[0] <= port <= VALID_PORT_RANGE[1]:
        return port
    return None

def rate_limited():
    """Ensure minimum time between accepted commands."""
    global _last_command_time
    with _last_command_lock:
        now = time.time()
        if now - _last_command_time < RATE_LIMIT_SECONDS:
            return True
        _last_command_time = now
        return False
