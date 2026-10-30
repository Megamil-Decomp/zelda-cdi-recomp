---
name: zeldas-cdi-validation
description: "Reproduzir falhas e comparar candidatos Zelda CD-i com saves copiados, probe TCP, métricas e checks de pacote. Usar para testes/diagnóstico do runtime e aceitação de entrega; build ou screenshot isolado não certifica gameplay."
---

# Validação Zelda CD-i

Ler [AGENTS](../../../AGENTS.md), [handoff](../../../docs/AI_HANDOFF.md) e [Validation.md](../../../docs/wiki/Validation.md) antes de abrir um runtime.

Identificar referência/candidato pelo catálogo e proveniência; definir aceite, entrada, duração e parada. Criar pasta de sessão ignorada, configuração própria e cópia de bateria; conferir o original antes/depois. Não usar saves pessoais diretamente. Manter porta livre e processo de teste identificado.

Armadilhas que mudam o resultado:

- `halted=1` com frames avançando e `held=0` pode ser STOP normal. Menu F1/Start é pausa do host; `held` é depuração. Não tratar os três como a mesma espera.
- `Probe.module_targets()` e `screenshot()` estacionam o guest e não retomam automaticamente. Não fazer captura de depuração no meio do replay/antes de testar saída normal sem controlar essa pausa.
- `snapshot()` consulta sem pedir pausa; ledger exige paginação completa e estável. `dropped=0` sozinho não comprova captura inteira.
- `--headless` também desativa persistência; SDL dummy não testa hardware de áudio, display ou controle. `Probe.click()` é para cursor do player, não qualquer cursor desenhado pelo jogo.
- Encerramento `-9` solicitado pelo harness não é crash espontâneo e não prova save normal. Registrar motivo/status/sinal e não limpar processos do usuário.

Executar suíte sintética e CTest aplicáveis; reproduzir o cenário com inputs reais, depois comparar intervalos válidos/monotônicos com `coverage_interval()`. Declarar BIOS, overflow, alinhamento de inputs e lacunas; não usar FPS, demo ou razão nativa como equivalência. Confirmar o percurso a 1x.

Aceitar somente o escopo testado. Conferir executável empacotado, dependências, assinatura, mínimo de sistema e saída/save. Cross-build Windows/Deck não substitui ensaio no alvo. Registrar evidências privadas e resumo/limites públicos antes de promover ou fechar issue. Esta skill não concede autorização de publicação nem amplia a tarefa para campanhas completas.
