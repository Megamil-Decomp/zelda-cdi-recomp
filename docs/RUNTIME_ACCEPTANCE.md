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

### 2026-10-12 — BIOS com seeds explícitas (runtime-faces/gamelon)

| Etapa | Faces | Wand | Evidência privada |
| --- | --- | --- | --- |
| Shell | Passou: `Play CD-i` visível, cursor/driver ativos, ~99,5% nativo (inclui BIOS) | Passou | `probes/*-shell-seeded/` |
| Entrada | Passou: press/release IKAT publicados e lidos pelo guest | Não testado | `probes/faces-launch/` |
| Carregamento | Passou: Philips → Animation Magic → título → `Game Menu` | Não testado | `probes/faces-timeline/` |
| Gameplay | Não testado (nenhum comando enviado no menu) | Não testado | — |
| Recompilação | Pós-clique, maioria interpretada: ~10,0M nativas vs ~28,8M interpretadas em 147 s (~26% nativo, inclui BIOS); `native_state`: 2 compilados, 1 ativo, 2 rejeições de identidade | Não testado | `faces-timeline/timeline.json` |

Builds anteriores sem seeds explícitas ficavam `held` antes do shell
(`probes/faces-shell*`). Em `pace=1`, o contador de quadros avançou ~20,5/s
durante a captura; a causa (pacing do driver `dummy`, custo do interpretador ou
das leituras TCP) não foi isolada. Zelda's Adventure não foi testado.
