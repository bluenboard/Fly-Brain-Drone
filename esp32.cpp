
/*
  FlyBrain robot: ESP32 sensor + motor controller
  Sensors:
    HC-SR04: TRIG 5, ECHO 18 (use a voltage divider on ECHO!)
    Left IR OUT: 32
    Right IR OUT: 33
  DRV8833:
    AIN1 25, AIN2 26
    BIN1 27, BIN2 14

  USB serial:
    ESP32 -> laptop: S,distance_cm,left_ir,right_ir
    Laptop -> ESP32: F, L, R, S
*/

const int TRIG_PIN = 5;
const int ECHO_PIN = 18;
const int IR_LEFT_PIN = 32;
const int IR_RIGHT_PIN = 33;

const int AIN1 = 25;
const int AIN2 = 26;
const int BIN1 = 27;
const int BIN2 = 14;

const bool IR_ACTIVE_LOW = true;
const float EMERGENCY_STOP_CM = 12.0;

unsigned long lastReport = 0;
unsigned long lastCommand = 0;
const unsigned long REPORT_INTERVAL_MS = 100;
const unsigned long COMMAND_TIMEOUT_MS = 700;

String commandBuffer = "";
char currentCommand = 'S';

int readIR(int pin) {
  int raw = digitalRead(pin);
  bool detected = IR_ACTIVE_LOW ? (raw == LOW) : (raw == HIGH);
  return detected ? 1 : 0;
}

float readDistanceCM() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(3);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  unsigned long duration = pulseIn(ECHO_PIN, HIGH, 25000UL);
  if (duration == 0) return -1.0; // No valid echo
  return duration * 0.0343 / 2.0;
}

void setMotors(bool leftForward, bool rightForward,
               bool leftOn, bool rightOn) {
  digitalWrite(AIN1, leftOn && leftForward ? HIGH : LOW);
  digitalWrite(AIN2, leftOn && !leftForward ? HIGH : LOW);
  digitalWrite(BIN1, rightOn && rightForward ? HIGH : LOW);
  digitalWrite(BIN2, rightOn && !rightForward ? HIGH : LOW);
}

void stopMotors() {
  setMotors(true, true, false, false);
}

void applyCommand(char cmd, float distanceCM) {
  // Local safety override: stop if an obstacle is very close
  // or the ultrasonic reading is invalid.
  if (distanceCM < 0 || distanceCM <= EMERGENCY_STOP_CM) {
    stopMotors();
    return;
  }

  switch (cmd) {
    case 'F': setMotors(true,  true,  true, true); break;
    case 'L': setMotors(false, true,  true, true); break;
    case 'R': setMotors(true,  false, true, true); break;
    default:  stopMotors(); break;
  }
}

void setup() {
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(IR_LEFT_PIN, INPUT);
  pinMode(IR_RIGHT_PIN, INPUT);

  pinMode(AIN1, OUTPUT);
  pinMode(AIN2, OUTPUT);
  pinMode(BIN1, OUTPUT);
  pinMode(BIN2, OUTPUT);

  stopMotors();
  Serial.begin(115200);
  lastCommand = millis();
}

void loop() {
  // Receive commands from Python
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      if (commandBuffer.length() > 0) {
        char cmd = commandBuffer.charAt(0);
        if (cmd == 'F' || cmd == 'L' || cmd == 'R' || cmd == 'S') {
          currentCommand = cmd;
          lastCommand = millis();
        }
        commandBuffer = "";
      }
    } else if (commandBuffer.length() < 10) {
      commandBuffer += c;
    }
  }

  float distanceCM = readDistanceCM();

  if (millis() - lastCommand > COMMAND_TIMEOUT_MS) {
    currentCommand = 'S'; // Stop if laptop communication stalls
  }

  applyCommand(currentCommand, distanceCM);

  if (millis() - lastReport >= REPORT_INTERVAL_MS) {
    int leftIR = readIR(IR_LEFT_PIN);
    int rightIR = readIR(IR_RIGHT_PIN);

    Serial.print("S,");
    Serial.print(distanceCM, 1);
    Serial.print(",");
    Serial.print(leftIR);
    Serial.print(",");
    Serial.println(rightIR);

    lastReport = millis();
  }

  delay(10);
}
