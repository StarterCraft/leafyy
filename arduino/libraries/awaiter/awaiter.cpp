#include <Arduino.h>
#include "awaiter.hpp"

SerialAwait::SerialAwait(Stream& stream) {
  this->stream = stream;
};

void SerialAwait::init() {
  while (!initialized)
  {
    if (stream.available())
    {
      initialized = true;
    }
    else
    {
      stream.println("STREAM NOT INITIALIZED");
      delay(1000);
    }
  }

  stream.print("AWAITING CONTENT, ");
  stream.println(numMessages);
};

void SerialAwait::handleMessage() {
  numMessages++;
  stream.print("AWAITING CONTENT, ");
  stream.println(numMessages);
};
