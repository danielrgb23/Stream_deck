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
