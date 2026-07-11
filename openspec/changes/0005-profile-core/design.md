# Design: 0005-profile-core

## ProfileManager
- Mantém o perfil ativo em RAM (ver `persistence-schema`)
- Resolve evento de `InputSource` (id lógico + tipo) → ação mapeada no perfil ativo
- Não conhece hardware concreto, só as interfaces `InputSource`/`DisplayDriver`/`HidTransport`

## HID — transporte abstrato (USB HID e BLE HID)

Nem todo modelo/chip tem USB nativo (ex: ESP32 WROOM-32 clássico não tem; ESP32-S3 tem). Em vez de
`ProfileManager` chamar diretamente uma lib de USB ou de BLE, ele depende de uma interface
`HidTransport`, com o mesmo espírito de `InputSource`/`DisplayDriver`:

```
interface HidTransport {
  bool begin();
  bool isConnected();
  void sendKey(KeyEvent event);
}
```

Implementações concretas:

| Implementação      | Quando usar                          | Biblioteca de referência       |
|--------------------|----------------------------------------|-----------------------------------|
| `UsbHidTransport`   | Chips com USB nativo (ESP32-S3)         | TinyUSB (`USBHIDKeyboard`)        |
| `BleHidTransport`   | Chips sem USB nativo (ESP32 WROOM-32)   | `ESP32-BLE-Keyboard` (NimBLE)      |

- A escolha da implementação é feita pela mesma flag de build já usada para o modelo/HAL
  (`HID_TRANSPORT=USB|BLE`), não em runtime — evita incluir as duas libs no mesmo binário sem
  necessidade.
- `ProfileManager` e o restante do core SHALL NOT importar `TinyUSB` nem `ESP32-BLE-Keyboard`
  diretamente — apenas a interface `HidTransport`.
- O canal serial de configuração (spec `serial-protocol`) permanece separado do `HidTransport` e
  continua sempre via USB-serial (CP2102/CH340 ou nativo), mesmo em devices que usam BLE HID para as
  teclas — ou seja, um device com WROOM-32 configura perfil por USB-serial normalmente, mas emite as
  teclas por BLE.
- Fila simples de eventos de teclado a enviar, para não travar o loop principal em caso de múltiplas
  teclas simultâneas — a fila é agnóstica de transporte, só chama `HidTransport::sendKey()`.
