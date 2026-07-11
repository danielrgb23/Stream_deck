# Change: 0007-feature-oled-status-display (BLOQUEADA por 0001-0005)

## Why
No modelo Streamer, a tela OLED central precisa mostrar qual perfil está ativo (nome/ícone simples),
já que não há tela por tecla.

## What Changes
- Implementa renderização de nome de perfil + indicador simples na `OledStatusDisplay`.
- Atualiza a tela ao trocar de perfil via encoder.

## Impact
- Depende de: 0004 (hal-interfaces), 0005 (profile-core)
- Só se aplica ao modelo Streamer (Essential não tem tela; Creator Pro usa `feature-desktop-app-sync`
  + touchscreen próprio, fora do escopo desta feature)
