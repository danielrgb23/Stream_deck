#include "hal/streamer/OledStatusDisplay.h"

#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Wire.h>

namespace {

const uint8_t SCREEN_WIDTH = 128;
const uint8_t SCREEN_HEIGHT = 32;
const int8_t OLED_RESET_PIN = -1; // sem pino de reset dedicado
const uint8_t OLED_I2C_ADDRESS = 0x3C;

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET_PIN);

} // namespace

void OledStatusDisplay::init() {
    display.begin(SSD1306_SWITCHCAPVCC, OLED_I2C_ADDRESS);
    display.clearDisplay();
    display.display();
}

void OledStatusDisplay::showProfile(const Profile &profile) {
    display.clearDisplay();
    display.setTextSize(2);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(0, 8);
    display.println(profile.name);
    display.display();
}

void OledStatusDisplay::clear() {
    display.clearDisplay();
    display.display();
}
