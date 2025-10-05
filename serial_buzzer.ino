const int buzzerPin = 8;       // change if you wired elsewhere
unsigned long beepEnd = 0;
bool buzzing = false;

void setup() {
  pinMode(buzzerPin, OUTPUT);
  digitalWrite(buzzerPin, LOW);
  Serial.begin(115200);        // must match Python
}

void loop() {
  // Handle timed beep stop
  if (buzzing && millis() > beepEnd) {
    noTone(buzzerPin);         // safe for both active/passive
    digitalWrite(buzzerPin, LOW);
    buzzing = false;
  }

  // Read serial
  if (Serial.available()) {
    char c = Serial.read();
    if (c == 'B') {
      // Simple beep: use tone for passive buzzer (1kHz), or digital HIGH for active buzzer
      unsigned long duration_ms = 3000; // default 3 s
      // If you want variable durations, read more bytes here (we keep it simple)
      // For passive buzzer, use tone():
      tone(buzzerPin, 1000);   // 1kHz tone
      beepEnd = millis() + duration_ms;
      buzzing = true;
      Serial.println("BUZZ ON");
    } else if (c == 'S') {
      noTone(buzzerPin);
      digitalWrite(buzzerPin, LOW);
      buzzing = false;
      Serial.println("BUZZ OFF");
    } else if (c == 'T') {
      // Short test beep
      tone(buzzerPin, 1500, 200);
      Serial.println("TEST TONE");
    }
  }
}
