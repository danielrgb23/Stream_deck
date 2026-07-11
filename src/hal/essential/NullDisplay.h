#pragma once

#include "hal/DisplayDriver.h"

// Essential nao tem tela. Implementacao no-op de DisplayDriver (spec
// hal-interfaces) para que o core (ProfileManager) funcione sem ifdefs de
// modelo.
class NullDisplay : public DisplayDriver {
public:
    void init() override {}
    void showProfile(const Profile &profile) override { (void)profile; }
    void clear() override {}
};
