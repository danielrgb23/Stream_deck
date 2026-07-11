# Xeeta Streamer — App Desktop

App desktop (specs `feature-desktop-app-sync`, `feature-software-presets`, `target-os-shortcuts` e
`app-launcher-volume-mixer`) para configurar o mapeamento de teclas do device via USB-serial, sem
precisar recompilar o firmware.

Referência arquitetural: MacroTouch (comunicação serial em tempo real, sistema de perfis) — adaptado
aqui para representar tecla física em vez de posição de touchscreen. Não é um fork; o protocolo e o
formato de perfil deste app são os definidos nas specs `serial-protocol`/`persistence-schema` do
firmware, não os do MacroTouch.

## Rodando

```bash
cd desktop-app
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python3 -m xeeta_streamer_app.app
```

## Estrutura

```
desktop-app/
├── xeeta_streamer_app/
│   ├── protocol.py        # envelope serial + struct Profile — espelha src/core/SerialProtocol.h e Profile.h
│   ├── serial_client.py   # detecção de device (PING/PONG) + GET/SET_PROFILE via pyserial
│   ├── device_worker.py   # I/O serial numa QThread separada (pyserial é bloqueante)
│   ├── profile_store.py   # persistência local em ~/.xeeta-streamer/profiles.json
│   ├── presets.py         # carrega pacotes de preset (spec feature-software-presets)
│   ├── keycodes.py        # tabela de keycodes (convenção Arduino Keyboard)
│   ├── named_actions.py   # ações multiplataforma (Copiar/Colar/etc, spec target-os-shortcuts)
│   ├── app_launcher.py    # combos HID reservados por posição de tecla (spec app-launcher-volume-mixer)
│   ├── installed_apps.py  # lista/abre apps instalados (Menu Iniciar no Windows, /Applications no Mac)
│   ├── installed_apps_panel.py  # painel arrastável de apps instalados
│   ├── hotkey_listener.py # atalho global do SO (pynput) para os combos reservados
│   ├── volume_control.py  # volume por processo (Windows/pycaw) ou master (Mac/osascript)
│   ├── editor_widget.py   # widget de edição de perfil (nome + SO-alvo + app de volume + 8 teclas)
│   ├── main_window.py     # janela principal + bandeja do sistema (conexão, perfil, editor, presets)
│   └── app.py             # entry point
└── presets/                # pacotes de preset (JSON), um arquivo por pacote
    ├── obs.json
    ├── premiere_davinci.json
    ├── home_office.json
    └── home_assistant.json
```

## Detecção de device

`serial_client.find_device()` varre as portas seriais disponíveis (`serial.tools.list_ports`) e testa
`PING`/`PONG` em cada uma — sem depender de VID/PID de USB, exatamente como pede a spec
`feature-desktop-app-sync`. Abrir a porta reseta o ESP32 (DTR/RTS), por isso há uma espera de boot
(`BOOT_SETTLE_SECONDS` em `serial_client.py`) antes do primeiro comando.

## Perfis locais

Formato documentado em `../docs/desktop-profile-format.md`. `profile_store.ProfileFile` é a única peça
que lê/escreve esse arquivo — a UI e o cliente serial nunca tocam o JSON diretamente.

## Presets

Cada arquivo em `presets/*.json` tem `name`, `target_software`, `notes` e uma lista `keys` (mesmo
formato de tecla usado no arquivo local de perfis). O combo "Importar preset..." na janela principal
aplica o preset ao editor — **local**, ainda não gravado no device até clicar em "Salvar". Para
adicionar um pacote novo, basta soltar um `.json` nessa pasta seguindo o mesmo formato.

## Sistema-alvo e ações nomeadas (Windows/Mac)

Cada perfil tem um campo "Sistema-alvo" (Windows ou Mac). Em cada tecla do editor, o combo de "ação
nomeada" (Copiar, Colar, Recortar, Desfazer, Refazer, Selecionar tudo, Salvar, Buscar, Fechar) preenche
automaticamente o modificador e a tecla certos para o sistema-alvo do perfil (`named_actions.py`) — ex:
"Copiar" vira `Ctrl+C` num perfil Windows e `Cmd+C` (bit `GUI`) num perfil Mac.

Editar manualmente os checkboxes de modificador ou o combo de tecla depois de escolher uma ação nomeada
desfaz essa associação (a tecla volta a "manual"). Trocar o sistema-alvo do perfil só re-resolve as
teclas que ainda estão associadas a uma ação nomeada — teclas mapeadas manualmente nunca são tocadas.
Isso é só uma conveniência do editor: o que chega ao device via `SET_PROFILE` continua sendo sempre
`modifiers`/`keycode` já resolvidos, igual a um mapeamento manual — o firmware não sabe nem precisa
saber que uma tecla veio de uma ação nomeada.

## Abrir app e volume por app (encoder repaginado)

Arraste um app instalado (painel à direita do editor) para uma tecla → aquela tecla passa a abrir esse
app; arraste para a área de "app de volume" do perfil → o encoder passa a controlar o volume desse app
enquanto o perfil estiver ativo. O encoder agora funciona assim: **rotação = volume, clique = troca de
perfil** (antes era o contrário).

Mecanismo: cada tecla/direção usa um combo de teclado reservado e raro (`Ctrl+Alt+Shift+F13..F20` para
teclas, `Ctrl+Alt+Shift+Seta cima/baixo` para volume) que o firmware emite via HID normalmente — o app
residente escuta esses combos como **atalho global do sistema operacional** (`pynput`,
`hotkey_listener.py`) e executa a ação de verdade localmente. Nenhuma mudança no protocolo serial.

No Mac, monitorar teclado globalmente exige permissão de Acessibilidade (System Settings → Privacy &
Security → Accessibility) para o processo Python/app — sem isso, os atalhos reservados não disparam
(atalhos digitados manualmente continuam funcionando normalmente, já que não dependem disso).

Volume por processo é real no Windows (Core Audio via `pycaw`); no Mac, a Apple não expõe API pública
equivalente — o ajuste sempre cai no volume master do sistema (aviso fixo na UI quando rodando no Mac).

O app continua rodando na bandeja do sistema ao fechar a janela principal — a conexão com o device e o
listener de atalho global seguem ativos. Use "Sair" no menu da bandeja para encerrar de verdade.

## Limitações desta fase

- App testado localmente até a construção da janela (`QT_QPA_PLATFORM=offscreen`); a detecção/sincronização
  com device real foi validada num ESP32 físico (modelo Essential) durante o bring-up de hardware — ver
  `docs/serial-protocol-manual-test.md`.
- Upload de ícone (`UPLOAD_ICON`, mencionado no proposal de `serial-protocol`) não está implementado —
  nenhum modelo atual tem tela por tecla.
- Sem ícones para os apps instalados (só nome + caminho) — melhoria futura, não bloqueia a feature.
- Volume por processo no Windows foi implementado e revisado, mas não testado em hardware Windows real
  (sem máquina disponível neste ambiente de desenvolvimento); o caminho Mac (`osascript`, volume master)
  foi testado ao vivo com sucesso.
