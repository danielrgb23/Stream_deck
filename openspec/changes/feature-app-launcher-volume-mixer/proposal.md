# Change: feature-app-launcher-volume-mixer

## Why
Hoje o device só consegue emitir atalhos de teclado — não existe jeito de uma tecla "abrir um app" ou
de o encoder "ajustar o volume de um app específico". Essas são as duas features mais pedidas depois do
mapeamento básico de teclas: abrir programas com um toque e controlar volume por aplicativo (ex: baixar
só o volume do Discord sem mexer no volume geral), sem precisar do usuário configurar isso manualmente
em cada app com atalho de teclado (a maioria nem tem).

## What Changes
- **Editor (app desktop)**: painel com os aplicativos instalados no sistema (Windows: atalhos do Menu
  Iniciar; Mac: `/Applications`), para arrastar:
  - para uma tecla física → cria a ação "abrir app" naquela tecla, naquele perfil;
  - para a área de "app de volume" do perfil → define qual app o encoder controla enquanto esse perfil
    estiver ativo.
- **Encoder repaginado**: a rotação passa a ajustar volume (do app vinculado ao perfil ativo, ou do
  volume master se nenhum app estiver vinculado); o clique passa a trocar de perfil (função que hoje é
  da rotação).
- **Mecanismo de disparo**: tanto "abrir app" quanto "ajustar volume" são sinalizados ao app desktop via
  combos HID reservados e raros (ex: `Ctrl+Alt+Shift+F13..F22`) que o firmware já sabe emitir (mesma
  infraestrutura de `HidTransport` que já existe) — o app residente escuta esses combos como atalhos
  globais do sistema operacional e executa a ação de verdade localmente. **Nenhuma mudança no protocolo
  serial nem no schema de perfil enviado ao device** além do já existente `SET_PROFILE`.
- **App desktop vira processo residente**: ícone na bandeja do sistema (system tray), mantém a detecção
  de device e o polling do perfil ativo (via `GET_ACTIVE_PROFILE`, comando já existente) mesmo com a
  janela principal fechada.
- **Volume por processo**: Windows via Core Audio (`pycaw`/`ISimpleAudioVolume`); Mac sem API pública
  equivalente — sempre cai no volume master, documentado como limitação conhecida da plataforma.

## Capabilities

### New Capabilities
- `app-launcher-volume-mixer`: ações "abrir app" (por tecla) e "volume por app" (por perfil), disparadas
  via combos HID reservados interceptados pelo app residente; app desktop como processo de bandeja;
  encoder com rotação = volume e clique = troca de perfil.

### Modified Capabilities
(nenhuma — aditivo. Não muda os requisitos de `feature-button-mapping`, `feature-desktop-app-sync` ou
`profile-core`; usa a mesma infraestrutura de `HidTransport`/`SET_PROFILE` já definida por eles. O
comportamento do encoder no firmware muda de implementação, mas a interface `InputSource`/`ProfileManager`
usada por ele não muda.)

## Impact
- Depende de: `feature-button-mapping`, `feature-desktop-app-sync`, `profile-core` (interface
  `HidTransport`/`ProfileManager` e o par CLK/DT/SW do encoder)
- Afeta o **firmware**: `src/core/ProfileManager.cpp` (rotação passa a emitir combo de volume via
  `HidTransport` em vez de trocar perfil; clique do encoder passa a trocar perfil)
- Afeta o **app desktop**: novo módulo de combos reservados, listener de atalho global, integração com
  Core Audio (Windows), enumeração de apps instalados, ícone de bandeja, novos campos no perfil local
  (`app_path` por tecla, `volume_mixer_app` por perfil)
- Não afeta: envelope do protocolo serial, schema binário de `Profile` enviado ao device
  (`SET_PROFILE` continua recebendo só `modifiers`/`keycode` — o combo reservado é só mais um valor
  possível desses dois campos, não um tipo de dado novo no wire)
