#pragma once

// Identificadores de modelo, selecionados via build_flags (-D DEVICE_MODEL=...)
// em platformio.ini. Nenhum outro arquivo deve redefinir estes valores.
#define ESSENTIAL 1
#define STREAMER 2
#define CREATOR_PRO 3

#ifndef DEVICE_MODEL
#error "DEVICE_MODEL nao definido. Compile com um dos envs de platformio.ini (essential, streamer, creator_pro)."
#endif

inline const char *deviceModelName() {
#if DEVICE_MODEL == ESSENTIAL
    return "essential";
#elif DEVICE_MODEL == STREAMER
    return "streamer";
#elif DEVICE_MODEL == CREATOR_PRO
    return "creator_pro";
#else
#error "DEVICE_MODEL com valor desconhecido"
#endif
}
