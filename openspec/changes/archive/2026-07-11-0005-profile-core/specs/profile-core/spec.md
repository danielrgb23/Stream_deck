# Spec Delta: profile-core

## ADDED Requirements

### Requirement: Resolução hardware-agnóstica de ações
O `ProfileManager` SHALL resolver eventos vindos de qualquer `InputSource` concreta em ações de teclado,
sem conhecer o tipo de hardware de origem do evento.

#### Scenario: Pressionar tecla física dispara atalho no PC
- **GIVEN** um perfil ativo com a tecla lógica 3 mapeada para `CTRL+F19`
- **WHEN** o usuário pressiona a tecla física correspondente à posição 3
- **THEN** o PC recebe o atalho `CTRL+F19` via o `HidTransport` configurado (USB ou BLE)

### Requirement: Transporte HID agnóstico (USB ou BLE)
O firmware SHALL emitir eventos de teclado através de uma interface `HidTransport` única, com
implementações concretas de USB HID e BLE HID, selecionadas via flag de build — sem que
`ProfileManager` ou qualquer código de core dependa diretamente de uma biblioteca de transporte
específica.

#### Scenario: Emitir tecla via USB (chip com USB nativo)
- **GIVEN** o firmware compilado com `HID_TRANSPORT=USB` para um chip com suporte nativo (ex: ESP32-S3)
- **WHEN** o `ProfileManager` resolve uma ação de teclado
- **THEN** a tecla é enviada ao PC via `UsbHidTransport` (TinyUSB)

#### Scenario: Emitir tecla via BLE (chip sem USB nativo)
- **GIVEN** o firmware compilado com `HID_TRANSPORT=BLE` para um chip sem suporte nativo (ex: WROOM-32)
- **WHEN** o `ProfileManager` resolve uma ação de teclado
- **THEN** a tecla é enviada ao PC via `BleHidTransport` (BLE Keyboard), sem nenhuma mudança de código em
  `ProfileManager`

### Requirement: Canal de configuração independente do transporte HID
O protocolo serial de configuração (spec `serial-protocol`) SHALL permanecer disponível via USB-serial
independentemente de qual `HidTransport` estiver ativo, permitindo configurar um device mesmo quando ele
emite teclas via BLE.

#### Scenario: Configurar um device que usa BLE HID
- **GIVEN** um device WROOM-32 com `HID_TRANSPORT=BLE`
- **WHEN** o app desktop se conecta via USB-serial para editar o perfil
- **THEN** a configuração funciona normalmente, sem interferir no `BleHidTransport` usado para as teclas
