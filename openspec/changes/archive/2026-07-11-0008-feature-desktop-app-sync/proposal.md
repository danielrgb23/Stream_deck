# Change: 0008-feature-desktop-app-sync (BLOQUEADA por 0001-0005)

## Why
É o app desktop em si — sem ele, o usuário final não configura nada além do que vier hardcoded no
firmware. Referência arquitetural principal: MacroTouch (Python + PyQt6, comunicação serial em tempo
real, sistema de perfis).

## What Changes
- App desktop detecta device via `PING` (spec `serial-protocol`).
- Lê/grava perfis do device via `SET_PROFILE`/`GET_PROFILE`.
- Persiste perfis localmente em JSON (spec `persistence-schema`) antes de enviar ao device.
- Editor de mapeamento (drag-and-drop), adaptado do MacroTouch para representar tecla física em vez de
  posição de touchscreen (Streamer/Essential) ou posição de touchscreen real (Creator Pro).

## Impact
- Depende de: 0002, 0003, 0005 (fundação completa)
- Maior superfície de feature do projeto — considerar quebrar em sub-changes ao detalhar
  (ex: 0008a-serial-client, 0008b-profile-editor-ui, 0008c-icon-upload) quando for implementar
