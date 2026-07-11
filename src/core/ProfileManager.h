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

    // Resolve um unico InputEvent ja obtido externamente (ex: um caller que
    // precisa inspecionar/logar o evento antes de despachar — ver
    // src/models/essential/main.cpp). Nao chamar isto E update() no mesmo
    // ciclo sobre a mesma InputSource: update() já faz seu próprio poll()
    // e drenaria a fila de novo, perdendo os eventos já consumidos aqui.
    void handleEvent(const InputEvent &event);

private:
    InputSource &input_;
    DisplayDriver &display_;
    HidTransport &hid_;

    void resolveKey(uint8_t logicalId, bool pressed);
    void switchToNextProfile();
    void switchToPreviousProfile();
};
