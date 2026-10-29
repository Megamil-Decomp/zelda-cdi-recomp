# Piloto REA — Faces of Evil

## Autorização e objetivo (2026-10-27)

Usuário autorizou investigação e melhorias autônomas com REA, sem perguntas durante sua ausência. Priorizar Faces of Evil e reduzir lacunas de análise/recompilação com evidência. Não alterar a mídia, saves originais ou checkout upstream, nem realizar commits/pushes.

## Plano

1. Registrar estado inicial, versões e proveniência; instalar ferramentas públicas de análise em diretório privado do projeto, sem modificar a configuração global do agente.
2. Validar REA/backend em amostra 68000 sintética antes de usar código comercial. Se o formato OS-9 não for aceito diretamente, investigar um adaptador privado que preserve offsets e metadados.
3. Relacionar resultados estáticos a rejeições do recompilador e rastros já existentes; coletar nova execução limitada se necessário, com NVRAM própria.
4. Automatizar o procedimento reproduzível e sua análise. Só promover alterações no runtime/recompilador após comparação e regressão sintética; usar staging/patches privados, preservando upstream.
5. Registrar resultados e limitações reais, inclusive se REA não suportar o alvo. Resultados de decompilação não são fonte original nem prova de equivalência.

## Aceitação e testes

- CLI REA executada de fato, com versão fixa e logs privados; backend identificado e teste sintético distinguindo sucesso, falha e suporte indisponível.
- Entradas comerciais, hashes, desassemblagens, pseudocódigo, bancos de análise e rastros exclusivamente em `build/` e `data/private/`.
- Ferramentas próprias testadas por `python3 -m unittest discover -s tests -v`, com dados sintéticos.
- Qualquer melhoria de cobertura deve comparar o mesmo cenário, contadores nativos/interpretados e falhas; não extrapolar boot para campanha completa.
- Qualquer correção de comportamento exige falha anterior reproduzida e verificação posterior. Na ausência de evidência, entregar diagnóstico/automação, sem alegar compatibilidade melhorada.
- Conferir mídia pelo lock local e estado do upstream ao final. Preservar alterações preexistentes e pacote entregue.

## Fontes a fixar no relatório privado

- REA: https://github.com/morluto/rea e pacote npm oficial `rea-agents`.
- Backend Ghidra, se usado: https://github.com/NationalSecurityAgency/ghidra.
- Upstream/core: commits e termos já auditados em `UPSTREAM_AUDIT.md`.

## 2026-10-28 — hipótese de tabela dentro da própria instrução

A emissão experimental de todas as entradas observadas falhou com `INVALID_STORE_EA`. REA/Ghidra classificou como dado um dos endereços especulados. Nos três sítios relacionados, a base PC-indexada fica na palavra de extensão do próprio `JMP`; a heurística lê essa palavra como primeira linha de tabela e começa a decodificar metadados como instruções.

Experimento: impedir essa inferência automática quando a base aponta para dentro da instrução de despacho, preservando o fallback existente para o destino calculado e as entradas comprovadas por execução. Aplicar somente ao staging privado com patch de contexto sob os termos upstream/core já auditados. Não alterar ISA, registradores ou temporização para contornar diagnósticos.

Aceitação adicional: fixture sintética deve reproduzir emissão inválida antes e passar depois; tabela legítima externa deve continuar descoberta. Emitir todas as seeds com os diagnósticos estritos ativos, executar CTest do frontend e comparar o cenário real até frame fixo, incluindo sequência de imagens, falhas e proporção nativa. Se a comparação divergir, manter o candidato isolado e registrar a divergência; não substituir o pacote entregue.
