# Design: 0004-hal-interfaces

## Interfaces
- `InputSource`: `poll()`, `getEvent()` — evento genérico (id lógico + tipo: press/release/rotate)
- `DisplayDriver`: `init()`, `showProfile(profile)`, `clear()`

## Implementações por modelo

| Modelo       | InputSource concreta                  | DisplayDriver concreta      |
|--------------|-----------------------------------------|--------------------------------|
| Essential    | `ButtonMatrixInput`                     | `NullDisplay` (no-op)          |
| Streamer     | `ButtonMatrixInput` + `EncoderInput`     | `OledStatusDisplay`            |
| Creator Pro  | `TouchscreenInput` (stub nesta fase)     | `TftTouchDisplay` (stub nesta fase) |

## Regra de dependência
`ProfileManager` e a emulação HID (spec `profile-core`) SHALL NOT importar nenhuma implementação
concreta — apenas as interfaces `InputSource`/`DisplayDriver`.

## Nota: HidTransport é uma abstração irmã, não parte desta spec
O transporte de saída de teclado (USB HID vs. BLE HID) é abstraído por uma interface separada,
`HidTransport`, definida e detalhada na spec `profile-core` (0005) — não faz parte de `DisplayDriver`
nem de `InputSource`, já que não é entrada nem exibição, é o canal de emissão de eventos HID pro PC.
