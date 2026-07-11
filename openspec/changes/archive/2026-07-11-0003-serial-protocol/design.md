# Design: 0003-serial-protocol

## Formato de pacote
`[protocol_version (1 byte)][command_id (1 byte)][payload_length (2 bytes)][payload (N bytes)]`

## Baud rate
Fixado em 115200 — decisão travada agora para não haver ambiguidade entre firmware e app desktop
implementados em momentos diferentes.

## Comandos desta fase
- `GET_VERSION` → retorna versão do firmware (semver) + versão do protocolo
- `PING` → retorna `PONG`, usado para o app desktop detectar presença do device

Comandos de feature (ex: `SET_PROFILE`, `GET_PROFILE`, `UPLOAD_ICON`) são definidos nas specs de feature
correspondentes, não aqui — esta spec só fixa o envelope do protocolo.
