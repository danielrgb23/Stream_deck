# Change: 0005-profile-core

## Why
Esta é a última spec de fundação — junta persistência, protocolo e HAL num núcleo funcional de troca de
perfil e emulação de teclado, sem ainda implementar nenhuma feature de produto.

Como nem todo chip da linha tem USB nativo (ESP32 WROOM-32 clássico não tem; ESP32-S3 tem), o transporte
de emulação de teclado precisa ser tratado como mais uma peça de hardware abstraída, e não fixado em USB
HID como nas primeiras versões desta spec.

## What Changes
- Implementa `ProfileManager` (cache RAM, troca de perfil, resolução tecla/gesto → ação).
- Define a interface `HidTransport`, com implementações concretas `UsbHidTransport` (TinyUSB) e
  `BleHidTransport` (BLE Keyboard/NimBLE), selecionadas via flag de build `HID_TRANSPORT=USB|BLE`.
- Integra com `persistence-schema` (0002), `serial-protocol` (0003) e `hal-interfaces` (0004).
- Mantém o canal de configuração serial sempre via USB, independente do transporte HID escolhido.

## Impact
- Affected specs: `profile-core` (nova)
- Depende de: 0001, 0002, 0003, 0004 — é a spec que fecha a fundação
- Bloqueia: todas as specs de feature (0006-0009)
- Modelos com USB nativo (ESP32-S3) usam `HID_TRANSPORT=USB` por padrão; modelos sem USB nativo
  (ESP32 WROOM-32) usam `HID_TRANSPORT=BLE` por padrão — ambos compilam do mesmo core.
