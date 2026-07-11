# Spec Delta: feature-software-presets

## ADDED Requirements

### Requirement: Importação de pacote de perfil pronto
O app desktop SHALL permitir importar um pacote de perfil pré-configurado e aplicá-lo a um perfil do
device, sem exigir mapeamento manual tecla por tecla.

#### Scenario: Aplicar preset do OBS
- **GIVEN** o usuário sem nenhum mapeamento configurado no perfil 1
- **WHEN** o usuário importa o pacote "OBS Studio" e aplica ao perfil 1
- **THEN** o perfil 1 passa a ter o mapeamento padrão do pacote (cortar cena, mutar mic, iniciar/parar
  live) sem edição manual
