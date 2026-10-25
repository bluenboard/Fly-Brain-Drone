// test_motors.ino
// Basic DRV8833 test with two DC motors

const int AIN1 = 25;
const int AIN2 = 26;
const int BIN1 = 27;
const int BIN2 = 14;

void stopMotors() {
  digitalWrite(AIN1, LOW);
  digitalWrite(AIN2, LOW);
  digitalWrite(BIN1, LOW);
  digitalWrite(BIN2, LOW);
}

void leftForward() {
  digitalWrite(AIN1, HIGH);
  digitalWrite(AIN2, LOW);
}

void leftReverse() {
  digitalWrite(AIN1, LOW);
  digitalWrite(AIN2, HIGH);
}

void rightForward() {
  digitalWrite(BIN1, HIGH);
  digitalWrite(BIN2, LOW);
}

void rightReverse() {
  digitalWrite(BIN1, LOW);
  digitalWrite(BIN2, HIGH);
}

void setup() {
  Serial.begin(115200);

  pinMode(AIN1, OUTPUT);
  pinMode(AIN2, OUTPUT);
  pinMode(BIN1, OUTPUT);
  pinMode(BIN2, OUTPUT);

  stopMotors();
  Serial.println("Motor test ready");
  delay(1000);
}

void loop() {
  Serial.println("Left motor: forward");
  leftForward();
  delay(1000);
  stopMotors();
  delay(1000);

  Serial.println("Left motor: reverse");
  leftReverse();
  delay(1000);
  stopMotors();
  delay(1000);

  Serial.println("Right motor: forward");
  rightForward();
  delay(1000);
  stopMotors();
  delay(1000);

  Serial.println("Right motor: reverse");
  rightReverse();
  delay(1000);
  stopMotors();
  delay(2000);
}