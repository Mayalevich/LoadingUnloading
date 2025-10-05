# serial_buzzer.py
import os
import time
import serial
import serial.tools.list_ports

BAUD = 115200
DEFAULT_TIMEOUT = 1.0

PREFERRED_KEYWORDS = (
    "usbmodem",   # Arduino on macOS
    "usbserial",  # FTDI/CP210x etc.
    "ttyacm",     # Linux Arduinos
    "ttyusb",     # Linux USB-serial
    "arduino",    # Description often includes this
    "slab",       # CP210x (Silicon Labs)
    "wch",        # CH340 clones sometimes say WCH
)


def _is_debug_console(p):
    dev = (p.device or "").lower()
    desc = (p.description or "").lower()
    return "debug" in dev or "debug" in desc


def find_arduino_port():
    """Find a connected Arduino-like serial port."""
    env_port = os.getenv("ARDUINO_PORT")
    if env_port:
        return env_port

    ports = list(serial.tools.list_ports.comports())
    print("Available serial ports:")
    for p in ports:
        print(f"  {p.device} - {p.description}")

    # Prefer known Arduino-like devices, skip debug console
    for p in ports:
        if _is_debug_console(p):
            continue
        dev = (p.device or "").lower()
        desc = (p.description or "").lower()
        if any(k in dev for k in PREFERRED_KEYWORDS) or any(
            k in desc for k in PREFERRED_KEYWORDS
        ):
            return p.device

    # Fallback: first non-debug port
    for p in ports:
        if not _is_debug_console(p):
            return p.device

    return None


class BuzzerController:
    """Encapsulates Arduino buzzer control via serial."""

    def __init__(self, port=None, baud=BAUD, timeout=DEFAULT_TIMEOUT, print_port_info=True):
        self.baud = baud
        self.timeout = timeout
        self.port = port or find_arduino_port()
        self.ser = None
        if print_port_info and not port:
            print(f"Chosen port: {self.port}")
        if self.port:
            self.connect(self.port)

        # For “hold 3 s” detection helper
        self._unauth_start = None
        self._buzzing = False
        self.REQUIRED_UNAUTH_SEC = 3.0
        self.COOLDOWN_SEC = 3.0
        self._last_buzz_time = 0.0

    # ---- Serial management ----
    def connect(self, port):
        try:
            if self.ser and self.ser.is_open:
                self.ser.close()
            self.ser = serial.Serial(port, self.baud, timeout=self.timeout)
            time.sleep(2)  # allow Arduino reset
            print(f"Connected to Arduino on {port}")
            self.port = port
        except Exception as e:
            print("Could not open serial port:", e)
            self.ser = None

    def send_cmd(self, cmd: str):
        """Low-level command sender."""
        if not self.ser or not self.ser.is_open:
            port = find_arduino_port()
            if port:
                self.connect(port)
        if not self.ser:
            print("No serial connection.")
            return False
        try:
            self.ser.write(cmd.encode("utf-8"))
            self.ser.flush()
            time.sleep(0.05)
            lines = []
            while self.ser.in_waiting:
                line = self.ser.readline().decode(errors="ignore").strip()
                if line:
                    lines.append(line)
            if lines:
                print("Arduino:", " | ".join(lines))
            return True
        except Exception as e:
            print("Serial write failed:", e)
            self.ser = None
            return False

    # ---- High-level commands ----
    def beep(self):
        """Trigger 3 s buzzer."""
        return self.send_cmd("B")

    def stop(self):
        """Stop buzzer immediately."""
        return self.send_cmd("S")

    def test(self):
        """Short 0.5 s test tone."""
        return self.send_cmd("T")

    # ---- New helper for “detected unauthorized for ≥3 s” ----
    def beep_if_held(self, unauthorized_detected: bool):
        """
        Call this every frame/tick with your detection flag.
        When 'unauthorized_detected' stays True for ≥3 s, buzz once for 3 s.
        """
        now = time.time()

        if unauthorized_detected:
            # Start or continue timer
            if self._unauth_start is None:
                self._unauth_start = now
            # If held long enough and not recently buzzed
            elif (
                now - self._unauth_start >= self.REQUIRED_UNAUTH_SEC
                and now - self._last_buzz_time >= self.COOLDOWN_SEC
            ):
                print("[ALERT] Unauthorized held 3 s → buzzing")
                self.beep()
                self._buzzing = True
                self._last_buzz_time = now
                self._unauth_start = None
        else:
            # Reset timer when back to authorized
            self._unauth_start = None
            self._buzzing = False

    def close(self):
        try:
            if self.ser:
                self.ser.close()
        except Exception:
            pass


# ---- quick manual test ----
if __name__ == "__main__":
    bc = BuzzerController()
    if not bc.port:
        print("No Arduino port found. Try: export ARDUINO_PORT=/dev/cu.usbmodem1101")
    else:
        print("Testing buzzer (short tone)...")
        bc.test()
        time.sleep(1)
        print("Simulating unauthorized 3 s hold...")
        for _ in range(6):
            bc.beep_if_held(True)
            time.sleep(0.5)
        bc.beep_if_held(False)
    bc.close()
