// test_sensors.ino
// ESP32 + HC-SR04 ultrasonic sensor + 2 IR obstacle sensors

const int TRIG_PIN = 5;
const int ECHO_PIN = 18;
const int LEFT_IR_PIN = 32;
const int RIGHT_IR_PIN = 33;

// Many IR obstacle modules output LOW when an
// obstacle is detected. Change this if your module differs.
const bool IR_ACTIVE_LOW = true;

float readDistanceCM() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);

  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  // Timeout prevents the ESP32 from waiting indefinitely.
  unsigned long duration = pulseIn(ECHO_PIN, HIGH, 30000);

  if (duration == 0) {
    return -1.0;  // No valid echo detected
  }

  return duration * 0.0343 / 2.0;
}

bool obstacleDetected(int pin) {
  int reading = digitalRead(pin);
  return IR_ACTIVE_LOW ? (reading == LOW) : (reading == HIGH);
}

void setup() {
  Serial.begin(115200);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(LEFT_IR_PIN, INPUT);
  pinMode(RIGHT_IR_PIN, INPUT);

  digitalWrite(TRIG_PIN, LOW);

  Serial.println("Sensor test started");
  Serial.println("Distance_cm,Left_IR,Right_IR");
}

void loop() {
  float distance = readDistanceCM();
  bool leftObstacle = obstacleDetected(LEFT_IR_PIN);
  bool rightObstacle = obstacleDetected(RIGHT_IR_PIN);

  Serial.print(distance);
  Serial.print(",");

  Serial.print(leftObstacle ? 1 : 0);
  Serial.print(",");

  Serial.println(rightObstacle ? 1 : 0);

  delay(200);
}