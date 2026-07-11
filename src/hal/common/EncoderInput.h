#pragma once

#include "hal/InputSource.h"
#include "hal/common/InputEventQueue.h"

// Le um encoder rotativo em quadratura (pinos A/B) + botao de push. Emite
// ROTATE_CW/ROTATE_CCW e PRESS/RELEASE para o botao do encoder (id logico
// ENCODER_BUTTON_LOGICAL_ID, de hal/InputEvent.h) — o que o ProfileManager
// faz com esses eventos e decisao dele (spec app-launcher-volume-mixer).
class EncoderInput : public InputSource {
public:
    EncoderInput(uint8_t pinA, uint8_t pinB, uint8_t pinButton);

    void begin() override;
    void poll() override;
    bool hasEvent() const override;
    InputEvent getEvent() override;

private:
    uint8_t pinA_;
    uint8_t pinB_;
    uint8_t pinButton_;
    uint8_t lastEncoded_ = 0;
    bool lastButtonState_ = false;

    InputEventQueue<8> queue_;
};
