# LoadShield — NuclearIC Challenge

This repository is part of the **F25 NuclearIC Challenge** organized by the [Ideas Clinic, University of Waterloo](https://github.com/IdeasClinicUWaterloo/F25-NuclearIC/tree/main).

It implements a **real-time personnel and safety monitoring system** that integrates **YOLOv11 object detection**, **Arduino-based sensors**, and **hardware feedback** to ensure **secure and stable nuclear material handling** during loading and unloading operations.

---

## 🔍 Overview

This project enhances operational safety in nuclear facilities by combining **machine learning**, **computer vision**, and **embedded sensing**.

- The **YOLOv11 model** detects and classifies personnel as *Authorized* or *Unauthorized*.  
- If *Unauthorized* personnel remain detected for **3 continuous seconds**, a **hardware buzzer** is activated via Arduino.  
- The **IR sensor** monitors for possible **radiation or heat leaks**, serving as an additional early-warning component.  
- The **IMU (BMX160)** ensures **stability and orientation consistency** during loading and unloading, detecting vibration or tilt anomalies that may indicate unsafe handling.  
- Together, these modules provide **visual**, **auditory**, and **sensor-based** safety assurance.

---

## 🧠 Key Features

- **Real-Time Object Detection:** YOLOv11 identifies personnel and tracks motion continuously.  
- **Safety Enforcement:** Unauthorized personnel trigger an audible buzzer alarm after 3 seconds.  
- **Infrared (IR) Leak Monitoring:** Detects temperature or radiation-related anomalies that may signal unsafe conditions.  
- **IMU-Based Motion Tracking:** Ensures the nuclear material remains level and stable during handling.  
- **Hardware Feedback Integration:** Combines Python control logic with Arduino-based hardware response.  
- **Visual + Audible Alerts:** Camera feed overlays with bounding boxes and an audible 3s buzzer alarm.  
- **Extensible Architecture:** Can integrate additional environmental sensors for radiation, pressure, or vibration.  

---

## 📂 Project Structure

```

LoadingUnloading/
├── main.py                     → YOLOv11 detection script
├── serial_buzzer.py            → Arduino serial communication
├── monitor_and_buzz.py         → Combines detection + sensor-based feedback
│
├── Arduino/
│   └── arduino_buzzer.ino      → Arduino firmware (buzzer + IR + IMU)
│
├── Loading_Unloading_Training_Files/
│   ├── best.pt                 → YOLO model weights (not public)
│   ├── data.yaml               → YOLO dataset configuration
│   └── train/                  → Training images and labels
│
└── README.md

```

---

## 🧩 System Architecture

```

YOLOv11 (Python)
│
├── main.py — Detects personnel
├── serial_buzzer.py — Sends 'B', 'S', 'T' commands via USB serial
│
▼
Arduino UNO (arduino_buzzer.ino)
├── B → Activate buzzer for 3s (unauthorized)
├── S → Stop buzzer
├── T → 0.5s test tone
│
├── IR Sensor → Monitors nuclear leak indicators (heat/radiation)
└── IMU (BMX160) → Detects improper tilt or unstable motion

```

---

## ⚙️ Dependencies

### Python
Install dependencies:
```

pip install ultralytics opencv-python pyserial

```

### Arduino
Required libraries:
- **DFRobot_BMX160** (IMU motion sensor)
- **Wire.h** (I2C communication)
- **DFRobot_BMX160.h** (for accelerometer/gyro support)

Compatible with both **active** and **passive** buzzers.

---

## 📊 Model Training

| Metric | Description |
|--------|--------------|
| **Model:** | YOLOv11 custom-trained on Authorized vs Unauthorized datasets |
| **Precision:** | 97.3% |
| **Recall:** | 96.8% |
| **mAP@0.5:** | 98.1% |

### Training Results
<img width="800" alt="confusion_matrix" src="https://github.com/user-attachments/assets/d078897d-22d9-4aad-b35b-c96c8c014457" />
<img width="800" alt="train_batch2" src="https://github.com/user-attachments/assets/4cde7f26-09ff-43df-a338-01b86f5f88ee" />
<img width="800" alt="results" src="https://github.com/user-attachments/assets/a38ba362-ba76-45ad-9e40-87acb348e066" />

---

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
3. Upload the firmware:
```

Arduino/arduino_buzzer.ino

```

### Step 3 – Run Detection
```

python main.py

```
- The camera feed will open.  
- Press **q** to quit.  
- Unauthorized personnel detected for 3 seconds → buzzer sounds.  

### Step 4 – Monitor + Arduino Connection
```

python monitor_and_buzz.py

```
This script continuously monitors the YOLO output, detects “Unauthorized” labels, reads IR/IMU sensor data, and sends commands to the Arduino.

---

## 🧪 Testing the Buzzer
You can manually test the Arduino connection:
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
- **Dataset:** Authorized vs Unauthorized personnel dataset  
- **Training Path:** `Loading_Unloading_Training_Files/train`  
- **Weights File:** `best.pt` (excluded from repo due to file size)  

---

## 🧱 Hardware Setup

| Component | Description |
|------------|-------------|
| **Arduino Uno/Nano** | Controls buzzer, IR, and IMU; communicates via serial |
| **Buzzer** | Active/passive buzzer on pin D5 |
| **IR Sensor** | Detects heat or radiation leaks via analog input A0 |
| **BMX160 IMU** | Monitors tilt and vibration stability via I2C (A4/A5) |

### Wiring Summary
```

D5  → Buzzer (+)
GND → Buzzer (−)
A0  → IR Sensor output
A4/A5 → SDA/SCL (IMU)

```

The IR sensor can be calibrated to trigger warnings for threshold heat/radiation values, while the IMU data ensures that the nuclear container remains stable and upright throughout the operation.

---

## 🏫 Acknowledgements

This project was developed as part of the **F25 NuclearIC Challenge** at the  
**University of Waterloo Ideas Clinic**.

Special thanks to:  
- **Ideas Clinic Staff** for dataset and technical guidance  
- **NuclearIC Challenge Team** for hosting and coordinating the competition  

Original challenge repository:  
[IdeasClinicUWaterloo/F25-NuclearIC](https://github.com/IdeasClinicUWaterloo/F25-NuclearIC)

---

## 🧾 License

This project is licensed under the **MIT License**.  
You are free to use, modify, and distribute it for educational or research purposes.

---

**Authors:**  
[Shunyu Yu](https://github.com/Mayalevich) — Lead Vision & Integration  
[Hank Lee](https://github.com/lee-cheng-han) — Hardware & Testing  
[Max Qiu](https://github.com/Sir7s) — Embedded Systems   
[Shiheng Wang](https://github.com/Wshhgugugu) — Model Training & Optimization  

📧 Contact: s362yu@uwaterloo.ca
