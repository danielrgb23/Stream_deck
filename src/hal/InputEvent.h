#pragma once

#include <stdint.h>

// Evento generico de entrada (spec hal-interfaces): id logico + tipo.
// ProfileManager (spec profile-core) resolve isto em uma acao sem saber se
// a origem foi um botao, um encoder ou um touchscreen.
enum class InputEventType : uint8_t {
    PRESS,
    RELEASE,
    ROTATE_CW,
    ROTATE_CCW,
};

struct InputEvent {
    uint8_t logicalId;
    InputEventType type;
};

// Id logico reservado para o botao de push do encoder — fora da faixa de
// teclas fisicas (0..MAX_KEYS_PER_PROFILE-1) para nao colidir com elas. Fica
// aqui (nao em EncoderInput, que e uma implementacao concreta de HAL) porque
// ProfileManager (core, spec profile-core) precisa reconhecer esse id sem
// depender de nenhuma InputSource concreta.
#define ENCODER_BUTTON_LOGICAL_ID 0xFE
