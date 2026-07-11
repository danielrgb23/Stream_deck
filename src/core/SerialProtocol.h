#pragma once

#include <stdint.h>

// Baud rate travado (spec serial-protocol) — firmware e app desktop
// (feature-desktop-app-sync) sempre usam este valor, sem negociacao.
#define SERIAL_BAUD_RATE 115200

// Versao do protocolo (primeiro byte de todo pacote). Incrementar apenas
// quando o ENVELOPE mudar de forma incompativel — comandos novos de feature
// nao exigem bump aqui.
#define SERIAL_PROTOCOL_VERSION 1

#define SERIAL_PACKET_MAX_PAYLOAD 250

// IDs de comando desta fase (envelope + PING/GET_VERSION). Comandos de
// feature (SET_PROFILE, GET_PROFILE, UPLOAD_ICON, ...) sao adicionados pelas
// specs de feature correspondentes, comecando em 0x10 para deixar espaço
// para comandos de infraestrutura aqui.
enum SerialCommand : uint8_t {
    CMD_PING = 0x01,
    CMD_PONG = 0x02,
    CMD_GET_VERSION = 0x03,
    CMD_VERSION_INFO = 0x04,

    // Exposicao minima do estado do perfil ativo (spec profile-core, canal
    // independente do HidTransport). Comandos de escrita/edicao de perfil
    // (SET_PROFILE, GET_PROFILE completo) sao de feature-button-mapping /
    // feature-desktop-app-sync, nao desta spec de fundacao.
    CMD_GET_ACTIVE_PROFILE = 0x05,
    CMD_ACTIVE_PROFILE_INFO = 0x06,

    // Comandos de feature-button-mapping: leitura/escrita de um perfil
    // completo pelo app desktop. Payload de CMD_GET_PROFILE e o prefixo de
    // CMD_SET_PROFILE e [profile_id (1 byte)]; payload de CMD_PROFILE_INFO e
    // de CMD_SET_PROFILE (apos o profile_id) e o struct Profile serializado
    // (src/core/Profile.h) byte a byte, sem padding.
    CMD_GET_PROFILE = 0x10,
    CMD_PROFILE_INFO = 0x11,
    CMD_SET_PROFILE = 0x12,
    CMD_SET_PROFILE_ACK = 0x13,
};

// Envelope de pacote (spec serial-protocol):
// [protocol_version (1 byte)][command_id (1 byte)][payload_length (2 bytes, little-endian)][payload (N bytes)]
struct SerialPacket {
    uint8_t protocol_version;
    uint8_t command_id;
    uint16_t payload_length;
    uint8_t payload[SERIAL_PACKET_MAX_PAYLOAD];
};

namespace SerialProtocol {

// Abre a porta serial de configuracao no baud rate fixo. Este canal
// permanece sempre via USB-serial, independente do HidTransport escolhido
// (spec profile-core).
void begin();

// Nao bloqueante — consome bytes disponiveis, remonta pacotes e despacha
// comandos. Chamar a cada iteracao de loop().
void poll();

} // namespace SerialProtocol
