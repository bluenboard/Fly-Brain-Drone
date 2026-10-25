// test_command_parser.ino
// Tests ESP32 serial command parsing without moving motors.
// Open Serial Monitor at 115200 baud and send F, L, R, or S.
// This verifies command reception only; it does not drive motors.

String commandBuffer = "";

void setup() {
  Serial.begin(115200);
  Serial.println("Command parser test ready. Send F, L, R, or S.");
}

void loop() {
  while (Serial.available() > 0) {
    char c = Serial.read();

    if (c == '\n' || c == '\r') {
      commandBuffer.trim();
      commandBuffer.toUpperCase();

      if (commandBuffer.length() > 0) {
        if (commandBuffer == "F" ||
            commandBuffer == "L" ||
            commandBuffer == "R" ||
            commandBuffer == "S") {
          Serial.print("Received valid command: ");
          Serial.println(commandBuffer);
        } else {
          Serial.print("Unknown command: ");
          Serial.println(commandBuffer);
        }
      }

      commandBuffer = "";
    } else if (commandBuffer.length() < 16) {
      commandBuffer += c;
    } else {
      commandBuffer = ""; // discard an unexpectedly long line
      Serial.println("Input too long; buffer cleared.");
    }
  }
}
