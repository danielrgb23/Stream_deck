# Xeeta Streamer — App Desktop

App desktop (specs `feature-desktop-app-sync` e `feature-software-presets`) para configurar o
mapeamento de teclas do device via USB-serial, sem precisar recompilar o firmware.

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
│   ├── editor_widget.py   # widget de edição de perfil (nome + 8 teclas)
│   ├── main_window.py     # janela principal (conexão + seletor de perfil + editor + import de preset)
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

## Limitações desta fase

- Testado localmente só até a construção da janela (`QT_QPA_PLATFORM=offscreen`, sem device físico
  conectado) — não foi possível validar a detecção/sincronização com um device real neste ambiente.
- Upload de ícone (`UPLOAD_ICON`, mencionado no proposal de `serial-protocol`) não está implementado —
  nenhum modelo atual tem tela por tecla.
