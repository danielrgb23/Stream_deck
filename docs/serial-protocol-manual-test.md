# Teste manual do protocolo serial (spec serial-protocol, task 3.5)

O envelope é binário, então um terminal de texto puro (`screen`, `PuTTY`) só é útil para *ver* que o
device respondeu, não para montar o pacote de request byte a byte com conforto. O jeito prático de
validar `PING`/`GET_VERSION` na mão é um script curto com `pyserial` (já instalado como dependência do
PlatformIO):

```bash
python3 - <<'EOF'
import serial, time

PORT = "/dev/tty.usbserial-XXXX"  # ajuste para a porta do seu device
BAUD = 115200

with serial.Serial(PORT, BAUD, timeout=1) as ser:
    time.sleep(2)  # aguarda o boot do ESP32 após abrir a porta

    # PING -> espera CMD_PONG (0x02) com payload "PONG"
    ser.write(bytes([1, 0x01, 0, 0]))  # protocol_version=1, command_id=PING, payload_length=0
    print("PING  ->", ser.read(8))

    # GET_VERSION -> espera CMD_VERSION_INFO (0x04) com payload [major, minor, patch, protocol_version]
    ser.write(bytes([1, 0x03, 0, 0]))
    print("VERSION ->", ser.read(8))
EOF
```

Saída esperada (com a versão atual `0.1.0` e `SERIAL_PROTOCOL_VERSION=1`):

```
PING  -> b'\x01\x02\x04\x00PONG'
VERSION -> b'\x01\x04\x04\x00\x00\x01\x00\x01'
```

Alternativa via `screen`/`PuTTY`: útil só para confirmar que o device está vivo e ecoando alguma coisa
(por exemplo, a linha de boot impressa em `setup()`), não para montar o pacote binário do protocolo.

## Validado em hardware real (2026-07-11)

Testado com o `DeviceClient` de `desktop-app/` (equivalente ao script acima, via API) contra um ESP32
genérico (CH340, board `esp32dev`) rodando o firmware `essential`:

```
ping: True
version: ('0.1.0', 1)
active profile: (0, 'Profile 0')
```

`SET_PROFILE`/`GET_PROFILE` também validados: perfil gravado via `SET_PROFILE` foi lido de volta
corretamente via `GET_PROFILE`, inclusive após a reconexão da porta serial (que reseta o ESP32) — confirma
que a escrita no NVS persiste através de reboot, não só na cache RAM.

Nota: o flash inicial falhou repetidamente ("chip stopped responding" parcialmente pela escrita da
imagem principal) enquanto o adaptador CH340 estava atrás de um hub USB — conectar direto numa porta do
Mac resolveu. Se `pio run -t upload` falhar de forma consistente e variável (ponto de falha diferente a
cada tentativa, escritas pequenas sempre OK), suspeite do hub/cabo antes de mexer em baud rate.
