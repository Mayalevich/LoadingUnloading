
# Loading & Unloading Subproblem — NuclearIC Challenge

This repository is part of the **F25 NuclearIC Challenge** organized by the [Ideas Clinic, University of Waterloo](https://github.com/IdeasClinicUWaterloo/F25-NuclearIC/tree/main).

It implements a **real-time personnel detection and alert system** that integrates **YOLOv11 object detection** and **Arduino hardware feedback** to identify unauthorized personnel during nuclear material loading and unloading operations.

---

## 🔍 Overview

This project enhances operational safety using a combination of **machine learning**, **computer vision**, and **embedded control**.

- The **YOLOv11 model** detects and classifies personnel as *Authorized* or *Unauthorized*.  
- If *Unauthorized* personnel are detected for **3 continuous seconds**, the **Arduino buzzer** activates automatically.  
- Provides both **visual** (bounding boxes) and **audible** (buzzer) alerts for real-time awareness.

---

## 🧠 Key Features

- **Object Detection:** YOLOv11 model distinguishes authorized vs unauthorized personnel.  
- **Live Feed:** OpenCV enables real-time object tracking.  
- **Hardware Integration:** Serial communication between Python and Arduino.  
- **Buzzer Feedback:** Arduino buzzer rings for 3 seconds when unauthorized personnel appear.  
- **Configurable Thresholds:** Detection sensitivity and timing easily adjustable.  
- **Optional Sensors:** Supports DFRobot BMX160 and IR modules for motion detection.  

---

## 📂 Project Structure

LoadingUnloading/  
├── main.py                     → YOLOv11 detection script  
├── serial_buzzer.py            → Arduino serial communication  
├── monitor_and_buzz.py         → Combines detection + hardware feedback  
│  
├── Arduino/  
│   └── arduino_buzzer.ino      → Arduino firmware  
│  
├── Loading_Unloading_Training_Files/  
│   ├── best.pt                 → YOLO model weights (not public)  
│   ├── data.yaml               → YOLO dataset configuration  
│   └── train/                  → Training images and labels  
│  
└── README.md  

---

## 🧩 System Architecture

YOLOv11 (Python)  
│  
├── main.py — Detects personnel  
├── serial_buzzer.py — Sends commands ('B', 'S', 'T')  
│  
▼  
Arduino UNO (arduino_buzzer.ino)  
├── 'B' → Buzz 3s (unauthorized)  
├── 'S' → Stop buzz  
└── 'T' → Test 0.5s buzz  

---

## ⚙️ Dependencies

### Python

Install dependencies:
```

pip install ultralytics opencv-python pyserial

```

### Arduino

- Library: **DFRobot_BMX160** (optional IMU)  
- Works with both **active** and **passive** buzzers  

---

### Model Training
<img width="3000" height="2250" alt="confusion_matrix" src="https://github.com/user-attachments/assets/d078897d-22d9-4aad-b35b-c96c8c014457" /> ![train_batch2](https://github.com/user-attachments/assets/4cde7f26-09ff-43df-a338-01b86f5f88ee)
<img width="2400" height="1200" alt="results" src="https://github.com/user-attachments/assets/a38ba362-ba76-45ad-9e40-87acb348e066" />



## 🔌 Usage

### Step 1 – Clone the Repository
```

git clone [https://github.com/Mayalevich/LoadingUnloading.git](https://github.com/Mayalevich/LoadingUnloading.git)
cd LoadingUnloading

```

### Step 2 – Connect Arduino
1. Plug in your Arduino via USB.  
2. Check connection:
```

ls /dev/cu.*

```
Example: `/dev/cu.usbmodem1101`  
3. Upload the sketch using Arduino IDE:  
`Arduino/arduino_buzzer.ino`

### Step 3 – Run Detection
```

python main.py

```
- The camera feed will open.  
- Press **q** to quit.  
- If “Unauthorized” is detected, the buzzer will sound for **3 seconds**.

### Step 4 – Monitor + Arduino Connection
```

python monitor_and_buzz.py

```
Continuously monitors YOLO output, detects “Unauthorized” labels, and sends commands to the Arduino.

---

## 🧪 Testing the Buzzer

You can test the Arduino connection manually:
```

python serial_buzzer.py

```

Expected Output:
```

Connected to Arduino on /dev/cu.usbmodem1101
Testing buzzer (short tone)...
Simulating unauthorized event -> beep 3s
Arduino: TEST 0.5s | BEEP 3s | BUZZ END

```

---

## 🧬 Model Information

- **Framework:** Ultralytics YOLOv11  
- **Dataset:** Authorized vs Unauthorized personnel images  
- **Training Path:** `Loading_Unloading_Training_Files/train`  
- **Weights File:** `best.pt` (excluded from repo due to size)  

---

## 🧱 Hardware Setup

| Component | Description |
|------------|-------------|
| **Arduino Uno/Nano** | Controls the buzzer and handles serial input |
| **Buzzer** | Active/passive buzzer on digital pin D5 |
| **IR Sensor (optional)** | Analog input on A0 |
| **BMX160 (optional)** | Accelerometer + Gyroscope via I2C (A4/A5) |

**Wiring Summary:**  
- D5 → Buzzer (+)  
- GND → Buzzer (−)  
- A4/A5 → SDA/SCL (IMU connection)  

---

## 🏫 Acknowledgements

This project was developed as part of the **F25 NuclearIC Challenge** at the  
**University of Waterloo Ideas Clinic**.

Special thanks to:  
- **Ideas Clinic Staff** for the dataset and framework guidance  
- **NuclearIC Challenge Team** for organizing and facilitating the challenge  

Original challenge repository:  
[IdeasClinicUWaterloo/F25-NuclearIC](https://github.com/IdeasClinicUWaterloo/F25-NuclearIC)

---

## 🧾 License

This project is licensed under the **MIT License**.  
You are free to use, modify, and distribute it for educational or research purposes.

---

**Author:** Shunyu Yu  
**University of Waterloo — Electrical and Computer Engineering**  
📧 asakura.h.madoka@gmail.com
