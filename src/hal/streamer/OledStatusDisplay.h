#pragma once

#include "hal/DisplayDriver.h"

// Tela OLED central do Streamer (Adafruit_SSD1306 + Adafruit_GFX, spec
// hal-interfaces). Mostra o nome do perfil ativo — a logica detalhada de
// exibicao pertence a spec feature-oled-status-display, esta implementacao
// cobre so o necessario para satisfazer a interface DisplayDriver.
class OledStatusDisplay : public DisplayDriver {
public:
    void init() override;
    void showProfile(const Profile &profile) override;
    void clear() override;
};
