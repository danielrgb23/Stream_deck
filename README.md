# Xeeta Streamer — OpenSpec: Roadmap Completo

Este pacote contém 9 changes no formato OpenSpec: 5 de fundação (implementar primeiro, nesta ordem) e
4 de feature (esqueletadas, bloqueadas até a fundação estar pronta).

## Estrutura

```
openspec/
├── specs/                                  # Specs ATIVAS (vazio até changes serem arquivadas)
└── changes/
    ├── archive/                            # Vazio por enquanto
    ├── 0001-build-scaffolding/              # Fundação
    ├── 0002-persistence-schema/             # Fundação — depende de 0001
    ├── 0003-serial-protocol/                # Fundação — depende de 0001
    ├── 0004-hal-interfaces/                 # Fundação — depende de 0001
    ├── 0005-profile-core/                   # Fundação — depende de 0002, 0003, 0004 (fecha a base)
    ├── 0006-feature-button-mapping/         # Feature — depende de 0002, 0003, 0004, 0005
    ├── 0007-feature-oled-status-display/    # Feature — depende de 0004, 0005
    ├── 0008-feature-desktop-app-sync/       # Feature — depende de 0002, 0003, 0005
    └── 0009-feature-software-presets/       # Feature — depende de 0006, 0008
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

Comandos de feature (`SET_PROFILE`, `GET_PROFILE`, `UPLOAD_ICON`, ...) são definidos pelas specs de
feature correspondentes, a partir de `0x10`, não por esta spec — ver `openspec/changes/0003-serial-protocol`.

Teste manual (ver `docs/serial-protocol-manual-test.md`).

### HAL (hardware abstraction layer)

`ProfileManager` (núcleo) só depende de três interfaces (`src/hal/InputSource.h`,
`src/hal/DisplayDriver.h`, `src/core/hid/HidTransport.h`) — nunca de uma implementação concreta. Cada
modelo pluga suas próprias implementações no `main.cpp` correspondente:

| Modelo       | `InputSource`                              | `DisplayDriver`               | `HidTransport` (padrão) |
|--------------|----------------------------------------------|-----------------------------------|-----------------------------|
| Essential    | `ButtonMatrixInput`                         | `NullDisplay` (no-op)             | `BleHidTransport`            |
| Streamer     | `ButtonMatrixInput` + `EncoderInput` (via `CompositeInputSource`) | `OledStatusDisplay` | `BleHidTransport`            |
| Creator Pro  | `TouchscreenInput` (stub)                   | `TftTouchDisplay` (stub)          | `UsbHidTransport`            |

`ButtonMatrixInput` mora em `src/hal/common/` porque é compartilhada entre Essential e Streamer;
implementações exclusivas de um modelo ficam em `src/hal/<modelo>/`. Cada `env` do `platformio.ini`
exclui via `build_src_filter` as pastas de HAL e de transporte HID que não pertencem a ele — assim o
binário de cada modelo só linka o que realmente usa (ex: Essential não linka `Adafruit_SSD1306`; Creator
Pro não linka a stack BLE).

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
