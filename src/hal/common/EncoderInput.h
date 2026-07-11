#pragma once

#include "hal/InputSource.h"
#include "hal/common/InputEventQueue.h"

// Le um encoder rotativo em quadratura (pinos A/B) + botao de push. Emite
// ROTATE_CW/ROTATE_CCW (usado pelo ProfileManager para trocar de perfil,
// spec profile-core) e PRESS/RELEASE para o botao do encoder. So usado no
// Streamer (spec hal-interfaces).
class EncoderInput : public InputSource {
public:
    // Id logico reservado para o botao do encoder — fora da faixa de teclas
    // fisicas (0..MAX_KEYS_PER_PROFILE-1) para nao colidir com elas.
    static const uint8_t ENCODER_BUTTON_LOGICAL_ID = 0xFE;

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
