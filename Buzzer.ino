/*
  IR + Buzzer + DFRobot BMX160 (Accel/Gyro/Mag)
  - IR photodiode on A0 (voltage divider with ~10kΩ to GND)
  - Buzzer on D5
  - BMX160 on I2C: SDA=A4, SCL=A5
*/

#include <Wire.h>
#include "DFRobot_BMX160.h"

const int IR_PIN       = A0;    // IR sensor input
const int BUZZER_PIN   = 5;     // Buzzer pin
const int IR_THRESHOLD = 200;   // IR trigger threshold
const int ACCEL_THRESHOLDx = 100; // mg threshold for movement
const int ACCEL_THRESHOLDy = 180;

DFRobot_BMX160 bmx160;

void setup() {
  Serial.begin(115200);
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);

  Wire.begin();  // I2C on A4/A5 (Arduino Uno/Nano)
  delay(100);

  if (!bmx160.begin()) {
    Serial.println("BMX160 init failed! Check wiring.");
    while (1) { delay(1000); }
  }
  Serial.println("BMX160 initialized successfully!");
  Serial.println("IR,ACC_X_mg,ACC_Y_mg,ACC_Z_mg,GYR_X_dps,GYR_Y_dps,GYR_Z_dps,MAG_X_uT,MAG_Y_uT,MAG_Z_uT");

  bmx160.setAccelRange(eAccelRange_4G);
}

void loop() {
  // --- Read IR sensor ---
  int irValue = analogRead(IR_PIN);

  // --- Read IMU data ---
  sBmx160SensorData_t accel;
  sBmx160SensorData_t gyro;
  sBmx160SensorData_t mag;
  bmx160.getAllData(&accel, &gyro, &mag);

  // --- Determine if motion threshold is exceeded ---
  bool motionDetected = (abs(accel.x) > ACCEL_THRESHOLDx) || (abs(accel.y) > ACCEL_THRESHOLDy);

  // --- Combine logic: IR or motion triggers buzzer ---
  if (irValue > IR_THRESHOLD || motionDetected) {
    analogWrite(BUZZER_PIN, 10);
  } else {
    analogWrite(BUZZER_PIN, 0);
  }

  // --- Print sensor data ---
  Serial.print(irValue); Serial.print(',');
  Serial.print(accel.x); Serial.print(',');
  Serial.print(accel.y); Serial.print(',');
  Serial.print(accel.z); Serial.print(',');
  Serial.print(gyro.x);  Serial.print(',');
  Serial.print(gyro.y);  Serial.print(',');
  Serial.print(gyro.z);  Serial.print(',');
  Serial.print(mag.x);   Serial.print(',');
  Serial.print(mag.y);   Serial.print(',');
  Serial.println(mag.z);

  delay(50); // ~20Hz sampling
}
