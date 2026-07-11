#pragma once

// Convencao de versionamento do firmware: semver (MAJOR.MINOR.PATCH).
//
// MAJOR - muda quando o schema de perfil (persistence-schema) ou o envelope do
//         protocolo serial (serial-protocol) quebram compatibilidade com
//         devices/apps ja em campo.
// MINOR - nova feature retrocompativel (ex: novo comando serial, novo tipo de
//         acao de perfil).
// PATCH - correcao de bug sem mudanca de contrato.
//
// Exposta em tempo de compilacao (estas constantes) e em tempo de execucao
// via comando serial GET_VERSION (spec serial-protocol).

#define FW_VERSION_MAJOR 0
#define FW_VERSION_MINOR 1
#define FW_VERSION_PATCH 0

inline const char *firmwareVersionString() {
    static char buf[16];
    snprintf(buf, sizeof(buf), "%d.%d.%d", FW_VERSION_MAJOR, FW_VERSION_MINOR, FW_VERSION_PATCH);
    return buf;
}
