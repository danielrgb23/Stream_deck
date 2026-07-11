#pragma once

#include "core/Profile.h"
#include "core/hid/HidTransport.h"
#include "hal/DisplayDriver.h"
#include "hal/InputSource.h"

// Nucleo do firmware (spec profile-core): resolve eventos de qualquer
// InputSource concreta em acoes de teclado do perfil ativo, emitidas via
// HidTransport, e atualiza o DisplayDriver quando o perfil ativo muda. Nao
// conhece hardware concreto — so estas interfaces + ProfileStore
// (persistencia, spec persistence-schema).
class ProfileManager {
public:
    ProfileManager(InputSource &input, DisplayDriver &display, HidTransport &hid);

    // Inicializa ProfileStore, InputSource, HidTransport e DisplayDriver, e
    // renderiza o perfil ativo carregado do NVS.
    void begin();

    // Chamar a cada iteracao de loop(): drena eventos da InputSource,
    // resolve em KeyAction do perfil ativo e envia via HidTransport.
    void update();

private:
    InputSource &input_;
    DisplayDriver &display_;
    HidTransport &hid_;

    void handleEvent(const InputEvent &event);
    void resolveKey(uint8_t logicalId, bool pressed);
    void switchToNextProfile();
    void switchToPreviousProfile();
};
