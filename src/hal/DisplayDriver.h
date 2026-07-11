#pragma once

#include "core/Profile.h"

// Interface de saida visual (spec hal-interfaces). ProfileManager (spec
// profile-core) SHALL NOT depender de nenhuma implementacao concreta
// (NullDisplay, OledStatusDisplay, TftTouchDisplay, ...) — apenas desta
// interface.
class DisplayDriver {
public:
    virtual ~DisplayDriver() = default;

    virtual void init() = 0;

    // Renderiza o estado do perfil ativo. O que exatamente e desenhado (nome,
    // icone, indicador) e decisao de cada implementacao concreta / spec de
    // feature (ex: feature-oled-status-display).
    virtual void showProfile(const Profile &profile) = 0;

    virtual void clear() = 0;
};
