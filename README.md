# Xeeta Streamer

Firmware (PlatformIO/ESP32, um core para os três modelos Essential/Streamer/Creator Pro) + app desktop
(Python/PyQt6) para um macro pad configurável, no formato de plano OpenSpec: 5 changes de fundação e 4
de feature. **As 9 changes já foram implementadas e arquivadas** — `openspec/specs/` contém as specs
ativas resultantes; `openspec/changes/archive/` tem o histórico de cada change.

- Firmware: ver seções abaixo (build, protocolo serial, HAL, `ProfileManager`/`HidTransport`).
- App desktop: ver `desktop-app/README.md`.
- Presets prontos (OBS, Premiere/DaVinci, Home Office, Home Assistant): `desktop-app/presets/`.

## Estrutura

```
openspec/
├── specs/                                  # Specs ativas (uma por capability, promovidas na archive)
└── changes/
    └── archive/                            # Histórico de cada change já implementada
src/                                        # Firmware (ver seção "Firmware — build")
desktop-app/                                # App desktop (ver desktop-app/README.md)
docs/                                       # Contratos de dados e procedimentos de teste manual
```

## Ordem de implementação

1. `0001-build-scaffolding` — sem isso, nada mais tem onde existir
2. `0002-persistence-schema`, `0003-serial-protocol`, `0004-hal-interfaces` — podem ser feitas em
   paralelo, todas só dependem de 0001
3. `0005-profile-core` — fecha a fundação, depende das três anteriores
4. A partir daqui, features: `0006` e `0007` podem ser paralelas; `0008` depende só da fundação;
   `0009` depende de `0006` e `0008` estarem prontas

## Arquitetura (resumo)

HAL (Hardware Abstraction Layer) + core desacoplado: `ProfileManager` e a emulação HID nunca conhecem
hardware concreto, apenas as interfaces `InputSource`/`DisplayDriver`. Cada modelo (Essential, Streamer,
Creator Pro) implementa sua própria versão dessas interfaces. Isso é o mesmo princípio usado por
firmwares de teclado sérios como QMK.

## Sobre clonar os repositórios de referência (Sparkpad-Arduino, MacroTouch)

Sim, vale clonar — mas como **material de referência**, não como base para fork direto:

- `Sparkpad-Arduino`: útil para extrair a lógica de debounce da matriz de botões, inicialização do
  encoder e uso da lib de OLED. Não dá pra usar a arquitetura dele como está, porque ele não separa
  hardware de lógica (tudo acoplado no mesmo `.ino`).
- `MacroTouch` (ESP32-Macro-Deck-with-PC-Control-Stream-Deck-DIY): útil para o **app desktop** —
  estrutura do protocolo serial, sistema de perfis em JSON, e o editor drag-and-drop. A parte de
  firmware dele (touchscreen) não se aplica ao Essential/Streamer, só ao Creator Pro.

Clone os dois num diretório `reference/` fora do repositório principal, leia o código, e porte apenas os
trechos relevantes para dentro da arquitetura em camadas definida aqui — não importe os repositórios
inteiros nem tente fazer merge de código deles com o seu core.

## Firmware — build

Projeto PlatformIO na raiz do repositório (`platformio.ini`). Um único `env` por modelo, todos
compilando a partir do mesmo `src/`:

```
pio run              # compila os três: essential, streamer, creator_pro
pio run -e streamer  # compila só um modelo
```

Estrutura de pastas do firmware:

```
src/
├── core/            # lógica desacoplada de hardware (ProfileManager, protocolo serial, versão)
├── hal/              # interfaces InputSource/DisplayDriver + implementações concretas por modelo
└── models/
    ├── essential/    # entrypoint (main.cpp) do modelo Essential
    ├── streamer/     # entrypoint do modelo Streamer
    └── creator_pro/  # entrypoint do modelo Creator Pro
lib/                  # bibliotecas privadas locais (dependências externas via lib_deps)
```

O modelo é selecionado exclusivamente pela flag de build `DEVICE_MODEL` (`ESSENTIAL` | `STREAMER` |
`CREATOR_PRO`, ver `src/core/DeviceModel.h`) — nunca por código-fonte duplicado. Cada `env` do
`platformio.ini` usa `build_src_filter` para incluir apenas o `models/<modelo>/` correspondente.

### Flash para o hardware

```bash
# 1. Descobrir a porta serial do device conectado
pio device list

# 2. Compilar e gravar no modelo/porta corretos (ajuste -e e --upload-port)
pio run -e essential -t upload --upload-port /dev/cu.usbserial-XXXX     # Mac/Linux
pio run -e essential -t upload --upload-port COM3                       # Windows

# 3. (opcional) Acompanhar o boot/log via monitor serial
pio device monitor -p /dev/cu.usbserial-XXXX -b 115200
```

`upload_speed = 115200` já está fixado em `platformio.ini` (seção `[env]`, vale pros três modelos) —
adaptadores CH340 (comuns em clones de ESP32 WROOM-32) costumam falhar no `upload_speed` padrão do
esptool (921600). Se o flash falhar de forma inconsistente mesmo assim (ponto de falha diferente a cada
tentativa, mas escritas pequenas como bootloader/partition table sempre OK), o suspeito mais provável é
o cabo/hub USB, não a velocidade — **conecte o device direto numa porta USB do computador, sem hub/dock
no meio**; foi exatamente isso que causou esse sintoma durante o desenvolvimento (ver
`docs/serial-protocol-manual-test.md`).

### Versionamento semântico

O firmware segue `MAJOR.MINOR.PATCH` (`src/core/Version.h`):

- **MAJOR** — quebra de compatibilidade no schema de perfil (`persistence-schema`) ou no envelope do
  protocolo serial (`serial-protocol`) com devices/apps já em campo.
- **MINOR** — nova feature retrocompatível (novo comando serial, novo tipo de ação de perfil, etc).
- **PATCH** — correção de bug sem mudança de contrato.

A versão é acessível em tempo de compilação (constantes `FW_VERSION_*`) e em tempo de execução via o
comando serial `GET_VERSION` (spec `serial-protocol`).

### Protocolo serial

Canal de configuração USB-serial, sempre em **115200 baud**, independente do transporte de teclas
(`HidTransport`, USB ou BLE — spec `profile-core`). Formato de pacote (`src/core/SerialProtocol.h`):

```
[protocol_version (1 byte)][command_id (1 byte)][payload_length (2 bytes, little-endian)][payload (N bytes)]
```

Comandos desta fase:

| command_id | Nome            | Payload                                                        |
|-----------:|------------------|-----------------------------------------------------------------|
| `0x01`     | `CMD_PING`       | vazio                                                            |
| `0x02`     | `CMD_PONG`       | `"PONG"` (ASCII, 4 bytes) — resposta ao `PING`                  |
| `0x03`     | `CMD_GET_VERSION`| vazio                                                            |
| `0x04`     | `CMD_VERSION_INFO`| `[fw_major][fw_minor][fw_patch][protocol_version]` — resposta ao `GET_VERSION` |
| `0x05`     | `CMD_GET_ACTIVE_PROFILE` | vazio                                                    |
| `0x06`     | `CMD_ACTIVE_PROFILE_INFO`| `[profile_id][name (16 bytes)]` — resposta ao `GET_ACTIVE_PROFILE` |

Comandos de feature (a partir de `0x10`, spec `feature-button-mapping`):

| command_id | Nome                | Payload                                                        |
|-----------:|----------------------|-------------------------------------------------------------------|
| `0x10`     | `CMD_GET_PROFILE`    | `[profile_id]`                                                     |
| `0x11`     | `CMD_PROFILE_INFO`   | `[profile_id][Profile serializado]` (33 bytes: `schema_version` + `name[16]` + `keys[8]` de `{modifiers, keycode}`, ver `src/core/Profile.h`) — resposta ao `GET_PROFILE` |
| `0x12`     | `CMD_SET_PROFILE`    | `[profile_id][Profile serializado]` — grava no NVS via `ProfileStore::saveProfile` |
| `0x13`     | `CMD_SET_PROFILE_ACK`| `[profile_id][status]` (`0` = ok, `1` = payload/id inválido) — resposta ao `SET_PROFILE` |

`UPLOAD_ICON` (mencionado no proposal de `serial-protocol`) não foi implementado — nenhum dos três
modelos tem tela por tecla nesta fase (Streamer usa só o nome do perfil no OLED central; Creator Pro é
stub). Fica em aberto para quando o Creator Pro sair de stub.

Teste manual (ver `docs/serial-protocol-manual-test.md`).

### HAL (hardware abstraction layer)

`ProfileManager` (núcleo) só depende de três interfaces (`src/hal/InputSource.h`,
`src/hal/DisplayDriver.h`, `src/core/hid/HidTransport.h`) — nunca de uma implementação concreta. Cada
modelo pluga suas próprias implementações no `main.cpp` correspondente:

| Modelo       | `InputSource`                              | `DisplayDriver`               | `HidTransport` (padrão) |
|--------------|----------------------------------------------|-----------------------------------|-----------------------------|
| Essential    | `DirectGpioInput` + `EncoderInput` (via `CompositeInputSource`) | `NullDisplay` (no-op) | `BleHidTransport` |
| Streamer     | `ButtonMatrixInput` + `EncoderInput` (via `CompositeInputSource`) | `OledStatusDisplay` | `BleHidTransport`            |
| Creator Pro  | `TouchscreenInput` (stub)                   | `TftTouchDisplay` (stub)          | `UsbHidTransport`            |

`ButtonMatrixInput` (varredura linha/coluna), `DirectGpioInput` (N botões cada um no seu próprio pino,
sem matriz) e `EncoderInput` moram em `src/hal/common/` por serem reaproveitáveis entre modelos;
implementações exclusivas de um modelo ficam em `src/hal/<modelo>/`. Cada `env` do `platformio.ini`
exclui via `build_src_filter` as pastas de HAL e de transporte HID que não pertencem a ele — assim o
binário de cada modelo só linka o que realmente usa (ex: Essential não linka `Adafruit_SSD1306`; Creator
Pro não linka a stack BLE).

`ButtonMatrixInput` exige fiação em matriz (linhas/colunas com diodos); `DirectGpioInput` é para quando
cada tecla tem seu próprio GPIO dedicado ligado direto ao GND (mais simples de montar em protótipo, ao
custo de usar mais pinos). Use a que bater com a fiação real — ligar botões diretos e tentar ler com
`ButtonMatrixInput` (ou vice-versa) não funciona; foi exatamente esse o bug encontrado e corrigido no
bring-up do protótipo Essential (ver pinout validado abaixo).

#### Pinout validado — protótipo Essential (5 botões + encoder, ESP32 WROOM-32)

```
Tecla 1 → GPIO4      Tecla 4 → GPIO14
Tecla 2 → GPIO5      Tecla 5 → GPIO16
Tecla 3 → GPIO13     Encoder CLK → GPIO21, DT → GPIO22, SW → GPIO25
```

Testado ponta a ponta em hardware real: os 5 botões, a rotação do encoder (`ROTATE_CW`/`ROTATE_CCW`) e o
clique do encoder (id lógico reservado `ENCODER_BUTTON_LOGICAL_ID = 0xFE`) disparam eventos distintos.
Ver `src/models/essential/main.cpp` — tem um flag `DEBUG_LOG_INPUT_EVENTS` (desligado por padrão) que
liga log de cada `InputEvent` + dump periódico do estado cru de cada pino, útil pra depurar fiação nova.

### ProfileManager e HidTransport

`ProfileManager` (`src/core/ProfileManager.h`) resolve eventos de qualquer `InputSource` em `KeyAction`
do perfil ativo (via `ProfileStore`, spec `persistence-schema`) e emite a tecla através de um
`HidTransport` — interface com duas implementações concretas, escolhidas em tempo de build pela flag
`HID_TRANSPORT` (`HID_TRANSPORT_USB` | `HID_TRANSPORT_BLE`, ver `src/core/hid/HidTransport.h`):

- `UsbHidTransport` (`src/core/hid/usb/`) — TinyUSB/`USBHIDKeyboard`, para chips com USB nativo (ESP32-S3
  → Creator Pro).
- `BleHidTransport` (`src/core/hid/ble/`) — `ESP32-BLE-Keyboard`/NimBLE, para chips sem USB nativo (ESP32
  WROOM-32 → Essential/Streamer).

O canal de configuração serial (`SerialProtocol`) continua sempre em USB-serial, independente do
`HidTransport` escolhido — inclusive expõe o estado do perfil ativo (`CMD_GET_ACTIVE_PROFILE` /
`CMD_ACTIVE_PROFILE_INFO`) sem tocar no transporte de teclas.

> **Nota de tamanho:** a stack BLE (NimBLE + ESP32-BLE-Keyboard) ocupa uma fatia grande da flash de 1.3MB
> do ESP32 clássico (~87-89% no build atual, sem nenhuma feature de produto ainda). Ao adicionar as
> features (0006+), vale monitorar o uso de flash do Essential/Streamer e considerar uma partition table
> customizada se necessário.

#### Encoder: rotação = volume, clique = troca de perfil (spec `app-launcher-volume-mixer`)

Papéis trocados em relação à fundação original: antes a rotação trocava de perfil e o clique não tinha
ação; agora `ROTATE_CW`/`ROTATE_CCW` emitem um combo HID reservado e fixo
(`Ctrl+Alt+Shift+Seta cima/baixo`, `src/core/ReservedVolumeCombo.h`) que o app desktop residente
intercepta como atalho global do SO para ajustar volume; o `PRESS` do botão do encoder
(`ENCODER_BUTTON_LOGICAL_ID`) agora chama `switchToNextProfile()`. Nenhuma mudança no protocolo serial —
o combo de volume é só mais um valor de `KeyEvent` emitido via `HidTransport`, como qualquer tecla.

Da mesma forma, cada tecla física tem um combo reservado próprio (`Ctrl+Alt+Shift+F13..F20`) usado só
quando o app desktop configura aquela tecla como "abrir app" — ver `desktop-app/README.md` para o
mecanismo completo (app residente + `pynput` + `pycaw`/`osascript`).

## App desktop — rodar em modo dev

```bash
cd desktop-app
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python3 -m xeeta_streamer_app.app
```

Isso roda direto do código-fonte (sem empacotar nada) — útil pra desenvolvimento, já que qualquer
mudança em `xeeta_streamer_app/*.py` aparece na próxima vez que você rodar o comando, sem rebuild. No
Mac, a primeira vez que o listener de atalho global (`pynput`) tentar rodar, o macOS provavelmente vai
pedir permissão de Acessibilidade para o processo Python — sem isso, os combos reservados de "abrir
app"/"volume" não disparam (o resto do app funciona normalmente).

## App desktop — gerar executável/instalador

Empacotado com [PyInstaller](https://pyinstaller.org/) — testado neste repositório e confirmado
funcionando (build real no Mac, `.app` executado com sucesso). **Precisa rodar em cada sistema
operacional alvo** (o PyInstaller não faz cross-compile: gerar o `.exe` do Windows exige rodar isto
numa máquina Windows, gerar o `.app` do Mac exige rodar num Mac):

```bash
cd desktop-app
source .venv/bin/activate       # mesmo venv de desenvolvimento (requirements.txt já instalado)
pip install pyinstaller
pyinstaller --name XeetaStreamer --windowed --noconfirm run.py
```

- **Mac**: gera `dist/XeetaStreamer.app` — um bundle `.app` de verdade, aparece na bandeja do sistema
  como qualquer outro app; pode ser aberto com `open dist/XeetaStreamer.app` ou copiado pra
  `/Applications`.
- **Windows**: gera `dist/XeetaStreamer/` (pasta com `XeetaStreamer.exe` + dependências) — distribua a
  pasta inteira, ou rode `pyinstaller --onefile` no lugar de `--windowed` sozinho pra gerar um único
  `.exe` (inicialização um pouco mais lenta, mas só um arquivo pra distribuir).

`run.py` (na raiz de `desktop-app/`, fora do pacote `xeeta_streamer_app/`) existe só pra isso: o
`xeeta_streamer_app/app.py` usa imports relativos (assume que faz parte do pacote), o que não funciona
se o PyInstaller apontar direto pra ele como script principal — o wrapper resolve isso com um import
absoluto.

Notas:
- `pycaw` (volume por processo no Windows) já é resolvido automaticamente pelo
  `pip install -r requirements.txt` — o `requirements.txt` marca essa dependência como
  `sys_platform == "win32"`, então só instala (e só é empacotada) ao rodar no Windows.
- A build gera `desktop-app/build/`, `desktop-app/dist/` e um `XeetaStreamer.spec` — todos ignorados
  pelo git (`.gitignore`); rode a build de novo a qualquer momento, não precisa versionar isso.
- A mesma exigência de permissão de Acessibilidade do modo dev (macOS) vale pro executável empacotado.
