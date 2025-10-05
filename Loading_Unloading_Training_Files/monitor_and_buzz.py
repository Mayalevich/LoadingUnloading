# monitor_and_buzz.py
# Run YOLO main.py, watch stdout, buzz Arduino on "Unauthorized"

import os, re, time, sys, subprocess
from serial_buzzer import BuzzerController

# --- tuning ---
MIN_INTERVAL_S = 3.0        # don't buzz more than once every N seconds
REQUIRED_FRAMES = 1         # buzz if Unauthorized appears in >= this many consecutive frames

# Regex: catches "1 Unauthorized" or "2 Unauthorizeds"
UNAUTH_COUNT_RE = re.compile(r'(\d+)\s+Unauthorized', re.IGNORECASE)
UNAUTH_WORD_RE  = re.compile(r'\bUnauthorized\b', re.IGNORECASE)

def count_unauthorized(line: str) -> int:
    m = UNAUTH_COUNT_RE.search(line)
    if m:
        try: return int(m.group(1))
        except: pass
    return 1 if UNAUTH_WORD_RE.search(line) else 0

def main():
    # Resolve main.py path relative to THIS file
    this_dir = os.path.dirname(os.path.abspath(__file__))
    main_path = os.path.join(this_dir, "main.py")
    if not os.path.exists(main_path):
        print(f"ERROR: main.py not found at {main_path}")
        # If yours is named differently, fix it here:
        # main_path = os.path.join(this_dir, "cv_run.py")
        sys.exit(1)

    # Start child in unbuffered mode
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    cmd = [sys.executable, "-u", main_path]

    print("Monitor started. Watching for 'Unauthorized' detections...")
    print("Press Ctrl+C to stop.\n")

    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1, env=env, cwd=this_dir
    )

    # Don't die if the serial port is busy now — we can buzz later once it frees up.
    bc = BuzzerController()  # if busy, it prints an error; later send_cmd() will retry
    last_buzz = 0.0
    unauthorized_streak = 0

    try:
        for line in proc.stdout:
            line = line.rstrip("\n")
            print(line)

            unauth = count_unauthorized(line)
            if unauth >= 1:
                unauthorized_streak += 1
            else:
                unauthorized_streak = 0

            now = time.time()
            if unauthorized_streak >= REQUIRED_FRAMES and (now - last_buzz) >= MIN_INTERVAL_S:
                ok = bc.beep()  # internally retries connection if it was busy earlier
                if not ok:
                    print("[warn] Could not buzz (port busy or not found). Will retry on next event.")
                last_buzz = now

    except KeyboardInterrupt:
        pass
    finally:
        try: proc.terminate()
        except: pass
        try: bc.close()
        except: pass
        print("Cleanup complete.")

if __name__ == "__main__":
    main()
