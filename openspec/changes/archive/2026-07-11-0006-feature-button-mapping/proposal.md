# Change: 0006-feature-button-mapping (BLOQUEADA por 0001-0005)

## Why
Primeira feature real de produto: permitir que o usuário final mapeie cada tecla física a uma ação
(atalho, combo, macro), via app desktop.

## What Changes
- App desktop envia mapeamento de perfil via protocolo serial (`SET_PROFILE`).
- Firmware persiste o mapeamento via `persistence-schema` (0002).
- Referência de repositório para o editor: MacroTouch (drag-and-drop de mapeamento), adaptado para
  representar botões físicos em vez de posições de touchscreen.

## Impact
- Depende de: 0002, 0003, 0004, 0005 (fundação completa)
