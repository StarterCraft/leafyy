#ifndef GREENYY
#define GREENYY


#include <Arduino.h>


namespace GreenyyArduino {
    class GreenyyCommand {
        public:
            GreenyyCommand(uint8_t associateWith, void (*function)());
            GreenyyCommand(char[] associateWith, void (*function)());

        private:
            uint8_t id;
            char strId[8];
            void (*function)();
    }


    class GreenyyPalette {
        public:
            GreenyyPalette();
            execute(uint8_t commandId);
            execute(char[] commandId);

        private:
            GreenyyCommand commands[256];
            uint8_t ix;
    }
}


#endif
