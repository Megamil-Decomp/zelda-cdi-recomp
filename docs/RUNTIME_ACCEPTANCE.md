# Aceitação do runtime local

## Plano — 2026-10-12

Validar o runtime compilado neste Mac antes de atribuir ao aplicativo capacidade
de executar um Zelda. Começar por Faces of Evil; repetir para os demais somente
com seus executáveis próprios disponíveis. Os testes não alteram a mídia.

1. Iniciar cada processo pelos vetores reais de reset da BIOS fornecida.
2. Esperar o shell com driver de entrada ativo, cursor e framebuffer publicados.
3. Capturar uma imagem privada do shell e identificar visualmente `Play CD-i`.
4. Em nova execução, mover o cursor por `set_input` e clicar pelo protocolo IKAT,
   sem escrever RAM, alterar registradores ou saltar para um endereço do jogo.
5. Observar progresso de disco, quadros, áudio, módulos nativos e falhas durante
   um intervalo finito; capturar a imagem final e contadores de cobertura.

O comando de pausa do debug server não permite continuar nesta versão. Por
isso, uma captura congelada termina a observação daquele processo. Os processos
pertencem ao teste e são encerrados por ele; nenhuma instância de terceiros é
encerrada. Preferências e bateria do teste ficam em `data/private/probes/`.

## Critérios

| Etapa | Evidência exigida | O que comprova |
| --- | --- | --- |
| Shell | Imagem visível, quadros avançando, cursor/driver ativos | BIOS/player inicializam |
| Entrada | Cursor alcança alvo; press/release IKAT aparecem | Caminho de entrada do guest |
| Carregamento | Disco progride e aplicação identificada visualmente | Aplicação começou a executar |
| Gameplay | Tela jogável, comandos respondem e sessão prolongada sem falha | Somente o cenário efetivamente observado |
| Recompilação | Módulos nativos ativos/dispatches e contadores separados | Cobertura nativa do intervalo observado |

Uma imagem do shell, mídia montada ou ausência de crash não comprova gameplay.
Percentuais globais incluem a BIOS e não equivalem à cobertura do jogo; registrar
também as diferenças antes/depois do clique. Interpretação precisa ser indicada.
Não usar hashes, offsets ou critérios particulares de Hotel Mario para aceitar
os jogos Zelda.

## Ferramenta própria

`scripts/probe_native_runtime.py` observa a API JSON TCP local e salva relatórios,
logs e PNGs privados. `--mode shell` captura o shell ao fim da observação;
`--mode launch --play-x X --play-y Y` faz o clique normal no alvo conferido pela
imagem do shell. Os limites de boot/observação/captura são finitos. O retorno 0
significa conclusão do procedimento, não aceitação de gameplay; o relatório
contém resultados e limitações separados.

## Resultados

### 2026-10-12 — Execução dos três títulos até introdução/menu

| Etapa | Faces | Wand | Adventure | Evidência privada |
| --- | --- | --- | --- | --- |
| Shell | Passou: `Play CD-i` visível, cursor/driver ativos | Passou | Passou | `probes/*-shell-seeded/` |
| Entrada | Passou: press/release IKAT lidos pelo guest | Passou: clique aciona carregamento | Passou: clique aciona carregamento | `probes/*-timeline/` |
| Carregamento | Passou: Philips → Animation Magic → título → `Game Menu` | Passou: Philips → Animation Magic → título → `Game Menu` | Passou: Philips → Título → FMV Gaspra → Pergaminho | `probes/*-timeline/` |
| Gameplay | Não testado (interação além do menu não enviada) | Não testado | Não testado | — |
| Recompilação | Pós-clique: ~9,0M nativas vs ~28,8M interpretadas (~24% nativo) | Pós-clique: ~9,0M nativas vs ~21,2M interpretadas (~30% nativo) | Pós-clique: ~8,6M nativas vs ~3,4M interpretadas (~71% nativo) | `probes/*-timeline/timeline.json` |

Em todos os títulos, o clique via IKAT em `Play CD-i` iniciou a reprodução
do disco e exibiu o fluxo real de abertura e menus/cenas. Os três executáveis
foram empacotados em `Zelda CD-i.app` e `Zelda-CDi-AppleSilicon.dmg` em `dist/`.
