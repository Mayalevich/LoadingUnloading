# main.py
# Live detection with YOLO; buzz Arduino only if "Unauthorized" persists for >= 3 seconds.

import cv2
import math
import time
from ultralytics import YOLO
from serial_buzzer import BuzzerController  # make sure serial_buzzer.py is beside this file

# -------- Config --------
MODEL_PATH = "/Users/jingyu/Documents/NIC_CV/F25-NuclearIC/Loading_Unloading_Subproblem/Loading_Unloading_Training_Files/best.pt"
CAM_INDEX = 0
BACKEND = cv2.CAP_AVFOUNDATION  # macOS
CONF_THRESH = 0.40

# -------- Init --------
yolo = YOLO(MODEL_PATH)

videoCap = cv2.VideoCapture(CAM_INDEX, BACKEND)
if not videoCap.isOpened():
    raise RuntimeError(
        "Unable to open camera 0. Grant Camera access to Terminal/VS Code in "
        "System Settings → Privacy & Security → Camera, then rerun."
    )

# Arduino buzzer controller
bc = BuzzerController()  # will auto-find /dev/cu.usbmodem* (or use ARDUINO_PORT env var)

# For optional motion helper (kept from your original helpers)
prev_flask_centre = None

# -------- Helpers you had (kept) --------
def get_target_id(result, target_class_name):
    target_id = None
    for class_id, class_name in result.names.items():
        if class_name == target_class_name:
            target_id = class_id
            break
    return target_id

def box_center(box):
    x1, y1, x2, y2 = map(int, box.xyxy[0])
    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2
    return cx, cy

def zone_select(x1, x2, y1, y2, frame):
    h, w = frame.shape[:2]
    return (int(x1 * w), int(y1 * h), int(x2 * w), int(y2 * h))

def detection_count(result, target_class_name):
    target_id = get_target_id(result, target_class_name)
    if target_id is None:
        return 0
    count = 0
    for box in result.boxes:
        if int(box.cls[0]) == target_id and float(box.conf[0]) >= CONF_THRESH:
            count += 1
    return count

def location_detect(result, target_class_name, zone_rect):
    target_id = get_target_id(result, target_class_name)
    if target_id is None:
        return 0
    count = 0
    for box in result.boxes:
        cls_id = int(box.cls[0])
        if cls_id != target_id or float(box.conf[0]) < CONF_THRESH:
            continue
        cx, cy = box_center(box)
        x1, y1, x2, y2 = zone_rect
        if x1 < cx < x2 and y1 < cy < y2:
            count += 1
    return count

def is_moving(result, target_class_name, dist_thresh_px):
    global prev_flask_centre
    target_id = get_target_id(result, target_class_name)
    if target_id is None and prev_flask_centre is None:
        return False
    for box in result.boxes:
        if int(box.cls[0]) == target_id and float(box.conf[0]) >= CONF_THRESH:
            cx, cy = box_center(box)
            if prev_flask_centre is None:
                prev_flask_centre = (cx, cy)
                return False
            dist = math.hypot(cx - prev_flask_centre[0], cy - prev_flask_centre[1])
            prev_flask_centre = (cx, cy)
            return dist > dist_thresh_px
    prev_flask_centre = None
    return False

# -------- Main loop --------
try:
    while True:
        ret, frame = videoCap.read()
        if not ret:
            continue

        # Process a single frame through YOLO (stream=True yields results iterator)
        results = yolo.track(frame, stream=True)

        # Accumulate per-frame status across YOLO result chunks
        unauthorized_in_frame = False

        for result in results:
            classes_names = result.names

            # Build a summary line like your logs
            unauthorized_count = detection_count(result, "Unauthorized")
            authorized_count = detection_count(result, "Authorized")

            if unauthorized_count > 0:
                unauthorized_in_frame = True

            # Pretty print (use actual frame size if you like)
            h, w = frame.shape[:2]
            size_str = f"{h}x{w}"
            if authorized_count > 0 or unauthorized_count > 0:
                parts = []
                if authorized_count > 0:
                    parts.append(f"{authorized_count} Authorized")
                if unauthorized_count > 0:
                    parts.append(f"{unauthorized_count} Unauthorized")
                detection_str = ", ".join(parts)
            else:
                detection_str = "(no detections)"
            print(f"0: {size_str} {detection_str}")

            # Draw boxes
            for box in result.boxes:
                conf = float(box.conf[0])
                if conf < CONF_THRESH:
                    continue
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cls = int(box.cls[0])
                class_name = classes_names[cls]

                # red for Unauthorized, green otherwise
                colour = (0, 0, 255) if class_name.lower() == "unauthorized" else (0, 255, 0)
                cv2.rectangle(frame, (x1, y1), (x2, y2), colour, 2)
                cv2.putText(frame, f'{class_name} {conf:.2f}', (x1, y1),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, colour, 2)

        # ---- 3-second persistence rule (buzz only if held >= 3s) ----
        # This delegates the timing to serial_buzzer.BuzzerController
        bc.beep_if_held(unauthorized_in_frame)

        # Show frame
        cv2.imshow("frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    pass
finally:
    try:
        videoCap.release()
    except:
        pass
    try:
        cv2.destroyAllWindows()
    except:
        pass
    try:
        bc.close()
    except:
        pass
