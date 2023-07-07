#include <awaiter.hpp>

SerialAwait smartStream = SerialAwait(Serial);

void setup() {
  Serial.begin(9600);
  smartStream.init();
}

void loop() {
  if (Serial.available()) {
    Serial.read();
    smartStream.handleMessage();
  }
}
