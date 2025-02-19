#ifndef IMAGE_HANDLER_H
#define IMAGE_HANDLER_H

#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ESP32Lib.h>
#include <VGA/VGA14Bit.h>




class ImageHandler {
public:
    ImageHandler(VGA14Bit &vga) : vga(vga) {}
    
    bool displayImage(const char* imageUrl, int x = 0, int y = 0) {
        HTTPClient http;
        http.begin(imageUrl);
        
        int httpCode = http.GET();
        if (httpCode == HTTP_CODE_OK) {
            // Get image data
            size_t size = http.getSize();
            uint8_t* buffer = new uint8_t[size];
            http.getStream().readBytes(buffer, size);
            
            // Convert to 14-bit pixels
            uint16_t* pixels = (uint16_t*)buffer;
            size_t pixelCount = size / 2;
            
            // Display image
            for (size_t i = 0; i < pixelCount; i++) {
                int px = x + (i % 320);
                int py = y + (i / 320);
                if (px < 640 && py < 480) {
                    vga.dotFast(px, py, pixels[i]);
                }
            }
            
            delete[] buffer;
            return true;
        }
        return false;
    }

private:
    VGA14Bit &vga;
};

#endif
