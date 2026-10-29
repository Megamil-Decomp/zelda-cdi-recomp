# Faces — regressões no primeiro trecho jogável

## Escopo e aceitação (2026-10-28)

Usuário relatou travamento ao atacar um objeto à direita no início do jogo e encerramento ocasional ao pular a abertura Philips no candidato REA. Introdução/menu não são aceitação de gameplay; percentual nativo e FPS não comprovam progresso da lógica.

1. Preservar logs fornecidos, crash report do processo e bateria por cópia privada, sem alterar originais. Identificar separadamente encerramento por sinal/falha, encerramento solicitado e lógica parada com vídeo ativo.
2. Reproduzir por inputs normais, primeiro no candidato e depois na referência quando necessário. Capturar estado anterior/posterior, destino, registradores e instruções; usar REA sobre o ponto relevante, sem supor que toda a falha decorre de cobertura.
3. Melhorar o launcher experimental para registrar comando/identidades, status de saída e sinal em um arquivo privado por sessão. Não ocultar aborts ou substituir leituras desconhecidas por valores inventados.
4. Corrigir somente uma causa comprovada em staging/patch reproduzível. Antes/depois precisam de regressão sintética e repetição do cenário real, inclusive a ação que falhava. Rodar `python3 -m unittest discover -s tests -v` e checks nativos pertinentes.
5. Se uma falha permanecer, registrar precisamente o que foi reproduzido e o que falta, sem declarar o candidato jogável. Manter mídia, saves originais, checkout upstream e pacote normal intactos; sem commits/pushes.

Evidência detalhada em `data/private/faces-regression/`. O relato sobre os outros títulos será respondido pela capacidade de análise e por validações efetivamente executadas, sem prometer que REA os torna compatíveis automaticamente.

## Decodificação especulativa e MMIO

O crash report confirmou leitura MMIO no preenchimento antecipado da janela do intérprete, antes de executar o operando. O patch 0008 limita a janela ao span RAM/ROM e exige que todos os bytes da instrução estejam presentes; não lê registradores para satisfazer especulação. Fetch fora desses spans ou instrução truncada continua falhando explicitamente. A geração de frame arquitetural para fetch em MMIO permanece não modelada; a exceção de operando real já existente deve continuar funcionando. Fixtures sintéticas verificam ambos os comportamentos e a preservação do status de interrupção adjacente.

## Próxima hipótese: entrega de interrupções

Investigar se uma segunda conclusão AP entra enquanto o handler anterior ainda publica seu estado. Conferir no manual específico do SCC68070 quando a máscara de prioridade deve mudar; não inferir apenas por semelhança com o 68000. Captura privada adicional registra SR e bytes de estado do driver nas leituras/escritas CIAP. Uma correção só será promovida após regressão sintética de máscara/frame e replay comparativo. Não alterar latências de AP ou ownership dos buffers para compensar um eventual erro de CPU.

Hipótese confirmada na entrada de IRQ do runtime e na especificação Philips de abril de 1993, seção 5.11, página 23. Patch 0009 eleva IPL e suprime trace depois de preservar o SR no frame. A captura anterior mostra o segundo atendimento AP consumindo o pedido ainda não limpo pelo primeiro; a correção sintética impede reentrada de mesmo nível. O replay com a correção passou da tela preta à área visível e continuou processando inimigos/colisões. O atendimento de prioridade superior e o retorno ao contexto anterior precisam continuar funcionando; são cobertos pela fixture sintética.
