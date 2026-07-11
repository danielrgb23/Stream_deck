# Spec Delta: app-launcher-volume-mixer

## ADDED Requirements

### Requirement: Listar aplicativos instalados para arrastar
O app desktop SHALL exibir uma lista dos aplicativos instalados no sistema operacional atual (Windows:
atalhos do Menu Iniciar; Mac: pacotes em `/Applications`), disponível para arrastar para uma tecla física
ou para a área de "app de volume" do perfil.

#### Scenario: Abrir o editor no Windows
- **GIVEN** o app desktop aberto no Windows
- **WHEN** o usuário abre o painel de aplicativos instalados
- **THEN** o painel lista os atalhos encontrados no Menu Iniciar, com nome de exibição

#### Scenario: Abrir o editor no Mac
- **GIVEN** o app desktop aberto no Mac
- **WHEN** o usuário abre o painel de aplicativos instalados
- **THEN** o painel lista os pacotes `.app` encontrados em `/Applications`

### Requirement: Ação "abrir app" por tecla física
O app desktop SHALL permitir arrastar um aplicativo instalado para uma tecla física de um perfil,
criando uma ação que abre esse aplicativo quando a tecla é pressionada. Essa ação SHALL ser sinalizada
ao app desktop através de um combo HID reservado e fixo por posição de tecla (`Ctrl+Alt+Shift+F13` a
`F20`), sem exigir nenhuma mudança no envelope do protocolo serial nem no schema binário de perfil
enviado ao device.

#### Scenario: Vincular um app a uma tecla
- **GIVEN** o editor de perfil aberto com o painel de aplicativos instalados visível
- **WHEN** o usuário arrasta "Spotify" para a tecla física 3
- **THEN** o perfil grava `app_path` apontando para o Spotify na tecla 3, e o `modifiers`/`keycode`
  enviado ao device via `SET_PROFILE` para essa tecla é o combo reservado correspondente à posição 3

#### Scenario: Pressionar a tecla abre o app vinculado
- **GIVEN** um perfil ativo no device com a tecla física 3 vinculada ao Spotify
- **WHEN** o usuário pressiona a tecla física 3
- **THEN** o device emite o combo HID reservado da tecla 3; o app desktop residente detecta esse combo
  via atalho global e abre o Spotify localmente

### Requirement: Vínculo de app de volume por perfil
O app desktop SHALL permitir arrastar um aplicativo instalado para a área de "app de volume" de um
perfil, definindo qual aplicativo terá seu volume ajustado pelo encoder rotativo enquanto esse perfil
estiver ativo no device. Perfis sem aplicativo vinculado SHALL usar o volume master do sistema.

#### Scenario: Vincular um app de volume a um perfil
- **GIVEN** o editor de um perfil aberto
- **WHEN** o usuário arrasta "Discord" para a área de "app de volume" do perfil
- **THEN** o perfil grava `volume_mixer_app` apontando para o Discord

#### Scenario: Girar o encoder sem app de volume vinculado
- **GIVEN** um perfil ativo sem `volume_mixer_app` definido
- **WHEN** o usuário gira o encoder
- **THEN** o volume ajustado é o volume master do sistema

### Requirement: Encoder — rotação ajusta volume, clique troca de perfil
O firmware SHALL emitir um combo HID reservado e fixo ao girar o encoder (um valor para sentido horário,
outro para anti-horário), e SHALL trocar o perfil ativo ao pressionar o botão do encoder — inversão dos
papéis anteriores (antes: rotação trocava perfil, clique não tinha ação).

#### Scenario: Girar o encoder ajusta volume
- **GIVEN** o device ligado, independente do perfil ativo
- **WHEN** o usuário gira o encoder no sentido horário
- **THEN** o device emite o combo HID reservado de "volume: subir"

#### Scenario: Clicar o encoder troca de perfil
- **GIVEN** o device no perfil "OBS"
- **WHEN** o usuário clica o botão do encoder
- **THEN** o device avança para o próximo perfil (mesmo comportamento que a rotação tinha antes),
  atualizando a tela OLED quando aplicável (modelo Streamer)

### Requirement: Ajuste de volume por processo (Windows) com fallback para master
No Windows, o app desktop SHALL ajustar o volume do processo vinculado ao perfil ativo via Core Audio
(`ISimpleAudioVolume`) ao detectar o combo reservado de volume. Se o processo vinculado não estiver em
execução, ou se nenhum processo estiver vinculado, SHALL ajustar o volume master do sistema.

#### Scenario: App de volume rodando
- **GIVEN** um perfil com `volume_mixer_app` = Discord, e o Discord em execução no Windows
- **WHEN** o app desktop detecta o combo reservado de "volume: descer"
- **THEN** o volume da sessão de áudio do Discord é reduzido, sem alterar o volume master

#### Scenario: App de volume vinculado mas não está rodando
- **GIVEN** um perfil com `volume_mixer_app` = Discord, e o Discord fechado
- **WHEN** o app desktop detecta o combo reservado de "volume: subir"
- **THEN** o volume master do sistema é aumentado (fallback)

### Requirement: Volume por processo no Mac cai sempre no volume master
No Mac, o app desktop SHALL sempre ajustar o volume master do sistema ao detectar os combos reservados
de volume, independente de `volume_mixer_app` estar preenchido — a Apple não expõe uma API pública
equivalente ao Core Audio do Windows para volume por processo.

#### Scenario: Perfil com app de volume vinculado, rodando no Mac
- **GIVEN** um perfil com `volume_mixer_app` definido, rodando no app desktop em um Mac
- **WHEN** o app desktop detecta um combo reservado de volume
- **THEN** o volume master do sistema é ajustado, e a UI indica que volume por processo não está
  disponível nesta plataforma

### Requirement: App desktop residente na bandeja do sistema
O app desktop SHALL continuar rodando em segundo plano, com um ícone na bandeja do sistema, ao fechar a
janela principal — mantendo a detecção do device e o acompanhamento do perfil ativo. O processo SHALL
encerrar apenas através da opção "Sair" no menu da bandeja.

#### Scenario: Fechar a janela principal
- **GIVEN** o app desktop conectado a um device, com a janela principal aberta
- **WHEN** o usuário fecha a janela principal (botão de fechar)
- **THEN** o processo continua rodando (ícone na bandeja visível), a conexão com o device permanece
  ativa, e as ações de "abrir app"/"ajustar volume" continuam funcionando

#### Scenario: Sair pelo menu da bandeja
- **GIVEN** o app desktop rodando em segundo plano (janela principal fechada)
- **WHEN** o usuário seleciona "Sair" no menu do ícone da bandeja
- **THEN** o processo encerra por completo
