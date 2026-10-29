# Steam Deck: próximos passos e controles

Avaliação em 2026-10-29; não houve execução em Deck/Proton nem build Linux nesta etapa. Manter o mesmo projeto. A estimativa é baixa a média para um perfil inicial de controles e média para uma experiência completa de interface, ciclo de vida e empacotamento.

## Sequência proposta

1. Validar o pacote Windows x64 em Windows real e reproduzir boot, inputs, transições, áudio e persistência dos três títulos.
2. Testar esse mesmo pacote no Deck via [Proton](https://partner.steamgames.com/doc/steamhardware/proton), inicialmente como programa local adicionado à biblioteca. Isso é um ensaio de compatibilidade, sem promessa de que já funciona.
3. Definir um perfil Steam Input que permita entrar/sair, selecionar jogo, usar o player CD-i e os menus sem teclado físico. [Steam Input permite emular teclado, mouse e gamepad](https://partner.steamgames.com/doc/features/steam_controller/legacy_mode).
4. Validar foco entre launcher/jogo, tela cheia, legibilidade, entrada simultânea, áudio, suspensão/retomada e saves. A Valve recomenda [acesso completo por controles e atenção aos launchers](https://partner.steamgames.com/doc/steamhardware/recommendations).
5. Após a prova e medição, avaliar build Linux x64 nativa com SDL e interface compartilhada navegável por controle. Um exportador Linux/Deck deve preservar a mesma seleção de candidatos, hashes e separação de dados. Não iniciar outro repositório ou substituir a lógica dos jogos.

## O que o código atual realmente oferece

O patch 0010 acrescenta analógico esquerdo com deadzone e menu por Start ao frontend SDL, além de D-pad/A/B, setas/WASD, Enter/Espaço/Z e X/Backspace. A navegação e os eixos têm testes sintéticos; falta ensaio com controle físico e no Deck. O ZIP Windows anterior ainda usa o frontend antigo.

O launcher Win32 tem navegação de teclado e mouse, sem leitura própria de gamepad. O patch 0010 separa entrega de mouse e captura: mouse livre com foco por padrão, captura opcional em F2. Movimento do cursor CD-i foi observado no Mac com o novo frontend; falta ensaio específico do trackpad/Proton. O launcher continua sendo um ponto pendente para navegação integral por controle.

## Perfil inicial proposto, ainda sem teste em hardware

| Controle Deck | Emulação sugerida | Objetivo |
| --- | --- | --- |
| D-pad / stick esquerdo | Setas | Movimento e seleção de lista |
| A | Enter | Ação/confirmar e botão padrão da interface |
| B | Backspace | Botão secundário do CD-i |
| Trackpad direito | Mouse | Navegação livre; captura opcional, ensaio Deck pendente |
| R2 / L2 | Clique esquerdo / direito | Botões 1/2 do CD-i |
| Start | Start ou F1 | Menu de opções do novo frontend |
| Botão traseiro opcional | F11 | Alternar tela cheia do runtime |

Aceitação: selecionar cada jogo, passar pelo player/menus, jogar um percurso conhecido, entrar/sair de inventário, fechar salvando e reabrir sem intervenção de teclado físico. Reproduzir as correções de fetch/IRQ e medir fallback no destino. Não usar processo vivo ou FPS isolado como aprovação. Nenhum perfil foi enviado ao Workshop; conteúdo/mídia comercial permanece privado.
