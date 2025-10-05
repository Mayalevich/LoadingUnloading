import time
import serial
import serial.tools.list_ports

BAUD = 115200
DEFAULT_TIMEOUT = 1.0

def find_arduino_port(vid_pid=None):
    # Prefer a heuristic: look for ports with "Arduino" in their description
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if "Arduino" in (p.description or "") or "ttyACM" in p.device or "ttyUSB" in p.device or "COM" in p.device:
            return p.device
    # fallback: return first available port
    return ports[0].device if ports else None

class BuzzerController:
    def __init__(self, port=None, baud=BAUD, timeout=DEFAULT_TIMEOUT):
        self.baud = baud
        self.timeout = timeout
        self.port = port or find_arduino_port()
        self.ser = None
        if self.port:
            self.connect(self.port)

    def connect(self, port):
        try:
            self.ser = serial.Serial(port, self.baud, timeout=self.timeout)
            time.sleep(2)  # wait for Arduino to reset
            print(f"Connected to Arduino on {port}")
            self.port = port
        except Exception as e:
            print("Could not open serial port:", e)
            self.ser = None

    def send_cmd(self, cmd: str):
        if not self.ser or not self.ser.is_open:
            # try to auto-find and reconnect
            port = find_arduino_port()
            if port:
                self.connect(port)
        if not self.ser:
            print("No serial connection.")
            return False
        try:
            self.ser.write(cmd.encode('utf-8'))
            self.ser.flush()
            # optional: read Arduino reply line
            time.sleep(0.05)
            while self.ser.in_waiting:
                line = self.ser.readline().decode(errors='ignore').strip()
                if line:
                    print("Arduino:", line)
            return True
        except Exception as e:
            print("Serial write failed:", e)
            self.ser = None
            return False

    def beep(self):
        return self.send_cmd('B')

    def stop(self):
        return self.send_cmd('S')

    def test(self):
        return self.send_cmd('T')

    def close(self):
        try:
            if self.ser:
                self.ser.close()
        except:
            pass

# Example usage:
if __name__ == "__main__":
    bc = BuzzerController()
    print("Testing buzzer (short tone)...")
    bc.test()
    time.sleep(1)
    print("Simulating unauthorized event -> beep 3s")
    bc.beep()
    time.sleep(4)
    bc.close()
