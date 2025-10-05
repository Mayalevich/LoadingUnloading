#include <Wire.h>
#include "DFRobot_BMX160.h"

// ---------- Pins ----------
const int BUZZER_PIN = 5;   // PWM-capable
const bool PASSIVE_BUZZER = false;  // true for passive buzzer (tone), false for active (analogWrite)

// ---------- Motion detection via delta (change) ----------
const float EMA_ALPHA = 0.02f;   // baseline smoothing factor (0..1). Smaller = slower baseline drift.
const int   DELTA_THRESH_MG = 150; // trigger when |accel - baseline| exceeds this (mg)
const int   OVER_COUNT_N = 3;      // need N consecutive "over" samples to turn ON
const int   UNDER_COUNT_N = 10;    // need N consecutive "under" samples to turn OFF

// If true, ignore auto motion; only serial 'B'/'T'/'S' controls buzzer.
const bool SERIAL_ONLY_MODE = false;

DFRobot_BMX160 bmx160;
bool imuOk = false;

// Serial timed buzz
unsigned long buzzerStartTime = 0;
unsigned long buzzerDuration  = 0;
bool serialBuzzing            = false;

// Auto buzz
bool autoBuzzing = false;
int  overCount   = 0;
int  underCount  = 0;

// Baseline (EMA)
float bx = 0, by = 0, bz = 0;
bool  baselineInit = false;

// Heartbeat
unsigned long lastBeat = 0;

// ---- Buzzer helpers ----
void buzzerOnPassive(unsigned int hz = 1000) { tone(BUZZER_PIN, hz); }
void buzzerOffPassive() { noTone(BUZZER_PIN); digitalWrite(BUZZER_PIN, LOW); }
void buzzerOnActive(uint8_t duty = 160) { analogWrite(BUZZER_PIN, duty); }
void buzzerOffActive() { analogWrite(BUZZER_PIN, 0); }

void buzzerOn(unsigned long duration_ms = 0, unsigned int hz = 1000) {
  if (PASSIVE_BUZZER) buzzerOnPassive(hz);
  else                buzzerOnActive(160);
  if (duration_ms > 0) {
    serialBuzzing   = true;
    buzzerStartTime = millis();
    buzzerDuration  = duration_ms;
  }
}
void buzzerOff() {
  if (PASSIVE_BUZZER) buzzerOffPassive();
  else                buzzerOffActive();
  serialBuzzing = false;
}

void setup() {
  Serial.begin(115200);
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);

  Wire.begin();
  Wire.setClock(400000);
  delay(100);

  if (bmx160.begin()) {
    imuOk = true;
    bmx160.setAccelRange(eAccelRange_4G);
    Serial.println("BMX160 initialized successfully!");
  } else {
    imuOk = false;
    Serial.println("BMX160 init FAILED (continuing without IMU).");
  }

  Serial.println("Ready: B=Beep(3s), T=Test(0.5s), S=Stop");
}

void loop() {
  // Heartbeat
  if (millis() - lastBeat >= 1000) {
    lastBeat = millis();
    Serial.println("[HB] alive");
  }

  // ---- Serial commands ----
  while (Serial.available() > 0) {
    char cmd = Serial.read();
    Serial.print("[RX] "); Serial.println(cmd);
    if (cmd == 'B') { buzzerOn(3000, 1000); Serial.println("BEEP 3s"); }
    else if (cmd == 'T') { buzzerOn(500, 1500); Serial.println("TEST 0.5s"); }
    else if (cmd == 'S') { buzzerOff(); autoBuzzing=false; overCount=underCount=0; Serial.println("STOP"); }
  }

  // End timed serial buzz
  if (serialBuzzing && (millis() - buzzerStartTime >= buzzerDuration)) {
    buzzerOff();
    Serial.println("BUZZ END");
  }

  // ---- Auto motion → buzz (if enabled) ----
  if (!SERIAL_ONLY_MODE && !serialBuzzing && imuOk) {
    sBmx160SensorData_t accel, gyro, mag;
    bmx160.getAllData(&accel, &gyro, &mag);

    float ax = accel.x;  // mg
    float ay = accel.y;
    float az = accel.z;

    // Initialize baseline once
    if (!baselineInit) { bx = ax; by = ay; bz = az; baselineInit = true; }

    // EMA update
    bx = (1.0f - EMA_ALPHA) * bx + EMA_ALPHA * ax;
    by = (1.0f - EMA_ALPHA) * by + EMA_ALPHA * ay;
    bz = (1.0f - EMA_ALPHA) * bz + EMA_ALPHA * az;

    // Deltas from baseline (motion)
    float dx = fabs(ax - bx);
    float dy = fabs(ay - by);
    float dz = fabs(az - bz);

    bool over = (dx > DELTA_THRESH_MG) || (dy > DELTA_THRESH_MG) || (dz > DELTA_THRESH_MG);

    if (over) {
      overCount++;
      underCount = 0;
    } else {
      underCount++;
      overCount = 0;
    }

    // Turn ON after N consecutive over-threshold samples
    if (!autoBuzzing && overCount >= OVER_COUNT_N) {
      autoBuzzing = true;
      if (PASSIVE_BUZZER) buzzerOnPassive(1000);
      else                buzzerOnActive(160);
      Serial.print("AUTO BUZZ ON | dX="); Serial.print((int)dx);
      Serial.print(" dY="); Serial.print((int)dy);
      Serial.print(" dZ="); Serial.println((int)dz);
    }

    // Turn OFF after M consecutive under-threshold samples
    if (autoBuzzing && underCount >= UNDER_COUNT_N) {
      autoBuzzing = false;
      buzzerOff();
      Serial.println("AUTO BUZZ OFF");
    }

    // (Optional) Debug line:
    // Serial.print("ax=");Serial.print((int)ax); Serial.print(" ay=");Serial.print((int)ay);
    // Serial.print(" az=");Serial.print((int)az); Serial.print(" | dx=");
    // Serial.print((int)dx); Serial.print(" dy="); Serial.print((int)dy);
    // Serial.print(" dz="); Serial.println((int)dz);
  }

  delay(10);
}

