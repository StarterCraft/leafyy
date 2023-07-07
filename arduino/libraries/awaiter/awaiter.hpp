#include <Arduino.h>

class SerialAwait
{
private:
	Stream stream;
    bool initialized = false;
    int numMessages = 0;

public:
	SerialAwait(Stream &stream);

    void init();

    void handleMessage();
}
