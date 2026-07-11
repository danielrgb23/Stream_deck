# Change: 0004-hal-interfaces

## Why
É esta spec que garante que os três modelos compartilhem o mesmo core. Sem essa interface definida
primeiro, cada modelo vira um fork de firmware, contrariando o objetivo de manter uma linha de produtos
com um único código-base.

## What Changes
- Define interface `InputSource` (entrada: botão, encoder, touch).
- Define interface `DisplayDriver` (saída: nenhuma tela, OLED, TFT touch).
- Implementa versões concretas mínimas para Essential e Streamer.
- Cria stubs vazios (compilam, sem lógica real) para o Creator Pro.

## Impact
- Affected specs: `hal-interfaces` (nova)
- Depende de: `build-scaffolding` (0001)
- Bloqueia: `profile-core` (0005)
