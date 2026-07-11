# Change: 0003-serial-protocol

## Why
O app desktop (feature futura) e o firmware precisam de um contrato de comunicação estável desde já,
mesmo antes de existir qualquer UI. Definir isso cedo evita que a primeira versão do app fique acoplada
a um formato improvisado que quebra na primeira mudança de feature.

## What Changes
- Define formato de pacote serial (com campo de versão de protocolo).
- Define baud rate fixo.
- Implementa dois comandos base: `GET_VERSION` e `PING`.

## Impact
- Affected specs: `serial-protocol` (nova)
- Depende de: `build-scaffolding` (0001)
- Bloqueia: `profile-core` (0005) e `feature-desktop-app-sync` (0008)
