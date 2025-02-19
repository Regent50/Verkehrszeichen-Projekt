#include <ESP32Lib.h>
#include <ESP32Video.h>
#include <VGA/VGA14Bit.h>

VGA14Bit vga;

// Define RGB pin arrays
const int redPins[] = {13, 12, 14};
const int greenPins[] = {27, 26, 25};
const int bluePins[] = {33, 32, 15};

const int hsyncPin = 4;
const int vsyncPin = 2;

void setup() {
    Serial.begin(115200);

    // Correct VGA initialization
    vga.init(vga.MODE320x240, redPins, greenPins, bluePins, hsyncPin, vsyncPin);

    vga.clear(vga.RGB(0, 0, 0));
    vga.setCursor(10, 10);
    vga.setTextColor(vga.RGB(255, 255, 255));
    vga.print("VGA Test");
}

void loop() {}
