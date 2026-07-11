#pragma once

#include "hal/DisplayDriver.h"

// Stub do Creator Pro (spec hal-interfaces): apenas compila, sem
// renderizacao real. Implementacao completa e trabalho futuro fora do
// escopo da fundacao.
class TftTouchDisplay : public DisplayDriver {
public:
    void init() override {}
    void showProfile(const Profile &profile) override { (void)profile; }
    void clear() override {}
};
