# Validação e diagnóstico

Um build, screenshot ou processo vivo é uma observação, não aceitação de gameplay. Começar pelo critério da issue e pela referência identificada, sem alterar PC/registradores/RAM para forçar o resultado.

## Preparar uma sessão

Registrar no relatório privado título/revisão, identidade do runtime e entradas, plataforma, configuração, pacing, passos, estado inicial e condição de parada. Ler o catálogo aceito e `<runtime>.build.json`; não selecionar executável por data de pasta. Usar configuração própria e uma **cópia** de NVRAM: `CDI_PLAYER_CONFIG_PATH` deve apontar para a pasta da sessão; a bateria fica ao lado conforme o runtime. Guardar o hash do save original antes/depois, sem publicá-lo. Se faltar uma bateria de referência, registrar que o estado inicial é novo, não inventar equivalência.

Escolher porta TCP livre e timeout finito. Conectar só ao processo iniciado/identificado para esse ensaio. `probe_native_runtime.py` valida a porta antes do launch e grava em `data/private/probes/`. Conferir `--help` para os parâmetros atuais; `--mode launch` exige coordenadas Play verificadas visualmente. `Probe.click()` foi feito para o cursor de hardware do player, não para qualquer cursor desenhado pelo jogo.

`--headless` desativa frontend **e persistência de bateria**; não serve para aceitar save/restore ou controles SDL. SDL com drivers `dummy` exercita caminhos de software, mas não testa áudio audível, display, mouse físico, gamepad ou foco reais. Testar o frontend e o destino separadamente.

## Três tipos de pausa que não devem ser confundidos

| Observação | Significado |
| --- | --- |
| `halted=1`, frames avançando, `held=0` | Pode ser STOP normal da CPU enquanto dispositivos continuam; sozinho não é travamento |
| Menu F1/Start aberto | Pausa do host: frontend retorna 2 ao loop principal, CPU/dispositivos não avançam, eventos/sinais continuam e áudio SDL pausa |
| `Probe.pause_stable()`, `module_targets()` ou `screenshot()` | Pausa de depuração: coleta consistente; esses métodos **não retomam automaticamente** o runtime |

`snapshot()` consulta estado sem solicitar pausa. `screenshot()` percorre scanlines e mantém a pausa; `module_targets()` também estaciona o guest para paginar o ledger. Capturá-los no meio do replay pode ser a causa da aparente espera seguinte. Colher evidência estacionada ao final ou estudar o protocolo de retomada da versão usada antes de continuar; não adivinhar comandos. Evitar esse tipo de captura antes de testar encerramento normal.

## Reproduzir e distinguir causas

Guardar stderr e status/sinal de saída. Erro de MMIO, espera de CD/áudio, foco/captura negada, fluxo de jogo e pausa de depuração são hipóteses distintas. A correção de reposição ADPCM é o patch 0004; o ACK IKAT genérico do patch 0003 não foi demonstrado como solução do erro de disco de Adventure. Ver [índice dos patches](../../scripts/patches/README.md).

Quando houver tela preta, consultar avanço de frames/CPU, `held`, drive/CIAP/áudio e sequência de inputs antes de chamá-la de crash ou transição normal. O fluxo livre ainda não explicado de Adventure continua aberto; não descartá-lo porque outro percurso passou. Preservar o primeiro caso reproduzível e criar fixture sintética se o contrato de hardware puder ser isolado.

Nos relatórios, distinguir saída voluntária `0`, erro espontâneo e encerramento solicitado pelo harness. Alguns replays históricos registram `-9` após captura final pausada: não são prova de crash e tampouco teste de saída normal. SIGTERM deve passar pelo caminho normal de NVRAM; se não responder, registrar timeout e o estado da sessão antes de qualquer limpeza do processo de teste. Não matar processos do usuário ou tratar encerramento forçado como save validado.

## Medir e comparar

Usar `coverage()` e `coverage_interval()` do probe para contadores válidos/monotônicos: `nativas / (nativas + interpretadas)`. A métrica atual inclui BIOS; não apresentá-la como cobertura exclusiva do jogo ou campanha. Resposta ausente não é zero; contadores reiniciados e intervalos sem instruções não dão percentual útil. Registrar overflow e capturas incompletas; faltas de dispatch e rejeições merecem análise própria.

Comparar referência/candidato com bateria e configuração equivalentes, inputs registrados e critérios por cenário. Documentar diferenças no frame de clique/alinhamento: imagens parecidas não provam equivalência determinística de CPU, ciclos ou áudio. Demo automática não prova que os comandos funcionaram. A aceitação em velocidade normal exige ensaio a **1x**, além dos replays acelerados úteis à investigação.

## Antes de promover

Executar a suíte sintética exigida, CTest do build afetado e cenário real aplicável. Conferir o **binário empacotado**, hashes de origem/final, dependências incluídas, assinatura e compatibilidade mínima declarada. Verificar menu/retomada, input, saída/save e reabertura quando afetados; usar save copiado. Windows/Deck/controle/áudio físicos precisam de ensaio próprio, não de inferência a partir do Mac.

Registrar resultado/limites em [PROGRESS.md](../PROGRESS.md), decisão em [DECISIONS.md](../DECISIONS.md) quando necessária, e preservar a versão anterior. Catálogos, Evidence, screenshots e mídia continuam privados; publicar somente o resumo autoral necessário. Procedimentos de entrega estão em [Development.md](Development.md).
