# Spec Delta: build-scaffolding

## ADDED Requirements

### Requirement: Build por modelo via flag única
O projeto SHALL compilar os três modelos (Essential, Streamer, Creator Pro) a partir de um único
repositório, selecionando o modelo apenas via flag de build `DEVICE_MODEL`, sem duplicar código-fonte.

#### Scenario: Compilar os três modelos
- **GIVEN** o repositório com os três `env` definidos no `platformio.ini`
- **WHEN** o comando `pio run` é executado sem argumento de env específico
- **THEN** os três binários (Essential, Streamer, Creator Pro) são gerados com sucesso

### Requirement: Versionamento semântico do firmware
O firmware SHALL expor sua versão no formato `MAJOR.MINOR.PATCH`, acessível em tempo de compilação e em
tempo de execução (via comando serial, definido na spec `serial-protocol`).

#### Scenario: Ler a versão em tempo de compilação
- **GIVEN** o firmware compilado a partir de qualquer um dos três `env`
- **WHEN** o código lê as constantes `FW_VERSION_MAJOR`/`FW_VERSION_MINOR`/`FW_VERSION_PATCH`
- **THEN** os três valores estão disponíveis em tempo de compilação, compondo a versão semântica atual
