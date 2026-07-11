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
    // Layout simples (spec feature-oled-status-display): rotulo pequeno em
    // cima, nome do perfil em destaque embaixo. Renderizacao e sincrona —
    // chamada diretamente por ProfileManager na troca de perfil, sem fila
    // ou delay, o que garante a atualizacao em bem menos de 200ms.
    display.clearDisplay();

    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(0, 0);
    display.println("Perfil ativo:");

    display.setTextSize(2);
    display.setCursor(0, 14);
    display.println(profile.name);

    display.display();
}

void OledStatusDisplay::clear() {
    display.clearDisplay();
    display.display();
}
