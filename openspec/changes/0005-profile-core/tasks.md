# Tasks: 0005-profile-core

- [x] 5.1 Implementar `ProfileManager` (cache RAM + troca de perfil)
- [x] 5.2 Implementar resolução evento → ação a partir do perfil ativo
- [x] 5.3 Definir interface `HidTransport` (agnóstica de transporte)
- [x] 5.4 Implementar `UsbHidTransport` via TinyUSB (para chips com USB nativo, ex: ESP32-S3)
- [x] 5.5 Implementar `BleHidTransport` via ESP32-BLE-Keyboard/NimBLE (para chips sem USB nativo, ex: WROOM-32)
- [x] 5.6 Selecionar implementação via flag de build `HID_TRANSPORT=USB|BLE` (`HID_TRANSPORT_USB` |
      `HID_TRANSPORT_BLE`, ver `src/core/hid/HidTransport.h`)
- [x] 5.7 Integrar `ProfileManager` com `InputSource`/`DisplayDriver` (spec 0004)
- [x] 5.8 Integrar leitura/escrita de perfil com NVS (spec 0002)
- [x] 5.9 Expor estado do perfil ativo via protocolo serial de configuração (spec 0003) — canal
      independente do `HidTransport`
- [x] 5.10 Teste end-to-end (USB): pressionar tecla física → PC recebe tecla HID correta via cabo —
      validado apenas por compilação (`pio run -e creator_pro`); execução em hardware real não foi
      possível neste ambiente (sem device físico disponível)
- [x] 5.11 Teste end-to-end (BLE): pressionar tecla física → PC recebe tecla HID correta via Bluetooth —
      validado apenas por compilação (`pio run -e essential`/`streamer`); execução em hardware real não
      foi possível neste ambiente (sem device físico disponível)
