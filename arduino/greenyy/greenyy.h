#ifndef GREENYY
#define GREENYY


#include <Arduino.h>


namespace LeafyyArduino {
    class LeafyyCommand {
        public:
            LeafyyCommand(uint8_t associateWith, void (*function)());
            LeafyyCommand(char[] associateWith, void (*function)());

        private:
            uint8_t id;
            char strId[8];
            void (*function)();
    }


    class LeafyyPalette {
        public:
            LeafyyPalette();
            execute(uint8_t commandId);
            execute(char[] commandId);

        private:
            LeafyyCommand commands[256];
            uint8_t ix;
    }
}


#endif
