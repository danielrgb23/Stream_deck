# Changes Arquivadas

Vazio por enquanto. A ordem esperada de implementação e arquivamento é:

**Fundação (implementar nesta ordem — cada uma depende da anterior):**
1. `0001-build-scaffolding`
2. `0002-persistence-schema`
3. `0003-serial-protocol`
4. `0004-hal-interfaces`
5. `0005-profile-core` (fecha a fundação)

**Features (só começar após 0001-0005 estarem arquivadas):**
6. `0006-feature-button-mapping`
7. `0007-feature-oled-status-display`
8. `0008-feature-desktop-app-sync`
9. `0009-feature-software-presets` (depende de 0006 e 0008)

Ao arquivar cada change, promova o conteúdo de `changes/<id>/specs/<capability>/spec.md` para
`openspec/specs/<capability>/spec.md`.
