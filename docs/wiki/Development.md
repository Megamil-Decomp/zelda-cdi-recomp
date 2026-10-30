# Desenvolvimento com IA

Aplicar ao pedido atual, sem ampliar escopo automaticamente. [Handoff](../AI_HANDOFF.md) identifica a base; [AGENTS](../../AGENTS.md) mantém os limites. Estas convenções não concedem permissão de commit/push, publicação, envio de mensagens ou edição do upstream.

## Ciclo de uma mudança

1. **Situar:** ler o estado recente, verificar `git status` e identificar título, runtime, cenário e dependências afetadas. Preservar alterações de outras pessoas/agentes. Usar o checkout apropriado; se abrir branch nova, adotar `codex/` salvo orientação diferente.
2. **Definir aceite:** problema observado, resultado esperado e teste que distingue ambos. Para alteração grande, registrar plano/aceitação/testes antes de editar. Distinguir fato, hipótese e proposta; não adiar trabalho independente por uma dúvida opcional.
3. **Mudar pouco:** código de host em `app/`; runtime/core por patch em cópia privada da revisão auditada. Nunca editar a árvore `upstream-cdirecomp/` sem autorização explícita. Referências de arquivos aceitos são imutáveis: uma mudança deve criar candidato novo.
4. **Verificar:** executar testes pertinentes e a suíte Python exigida. Regressões de CPU/hardware precisam de fixture sintética que reproduza o contrato, preferencialmente falhando no anterior. Em correção visual/documental pequena, inspeção/compilação/links podem ser suficientes; não criar testes que só repetem o texto ou a implementação.
5. **Comparar:** quando afetar execução, usar cenário privado com mesmo estado inicial, bateria copiada e inputs registrados. Preservar a referência e relatar diferenças. Aumentar cobertura não basta para promover; ver [validação](Validation.md).
6. **Entregar:** atualizar o mínimo necessário de DECISIONS/PROGRESS e backlog, conferir o diff e relatar resultados reais. Dentro da autorização vigente, criar commit focado com problema/efeito e validação; não incluir arquivos privados nem binários por conveniência.

Uma falha de ferramenta deve produzir diagnóstico antes de repetir a mesma operação. Reduzir o experimento ou corrigir entrada/ambiente; não desativar verificações para obter sucesso. Interromper a tentativa dependente se faltar mídia, identidade, licença aplicável ou referência; continuar partes independentes possíveis e informar a lacuna concreta.

## Dados, dependências e testes

- Mídia e BIOS originais são somente leitura. `roms/`, `bios/`, `data/private/`, `build/` e `dist/` permanecem ignorados. Hashes de mídia, seeds reais, dumps, logs, screenshots derivados e código comercial gerado ficam privados; resumos públicos contêm apenas resultados e limites necessários.
- Manter termos/proveniência do upstream/core. MIT do código próprio não relicencia o conjunto nem o contexto dos patches. Ver [auditoria](../UPSTREAM_AUDIT.md).
- Não atualizar silenciosamente REA/Ghidra/SDL/compilador para “o mais recente”. Fixar versão/origem/identidade no relatório privado e revalidar comportamento se mudar a dependência.
- Testes próprios: `python3 -m unittest discover -s tests -v`. Diferenciar passou, falhou e pulado por dependência ausente. Para runtime candidato, `ctest --test-dir CAMINHO_DO_BUILD --output-on-failure`, usando o diretório de build identificado pela proveniência.
- Patches mantêm o espaço de contexto do unified diff; `.gitattributes` já trata isso. Não remover esses espaços para “corrigir” whitespace, nem aplicar patch cegamente sobre uma cópia que já o contém.

## Construir e empacotar sem perder a referência

`build_native_runtimes.py` gera uma base e substitui seu staging; não é um comando inocente de atualização do candidato aceito. Examinar primeiro os arquivos referidos por `<runtime>.build.json`.

`build_player_ui.py` parte de entradas aceitas e cria variantes do host, conferindo patches/headers/SDL. Ele **não** descobre novas entradas do jogo; um resultado em `runtime-catalog-all.json` ainda é candidato. Nova cobertura passa pelo [REA](REA.md), emissão estrita e comparação própria.

`build_macos_app.py --runtime-catalog` exige exatamente os três títulos e identidades completas. Conferir separadamente hash de origem e do executável final: rpaths/assinatura alteram bytes. Usar destino de teste em diretório ignorado e manter app anterior recuperável. Validar dependências internas/sistema, assinatura, versão mínima, manifesto e um cenário do binário efetivamente empacotado. Repetir aceitação na plataforma alvo; cross-compilar não testa o sistema de destino.

Somente após aceite atualizar o catálogo privado selecionado e promover o app. Os exportadores copiam a seleção aceita e mídia correspondente, sem saves pessoais; não são distribuidores públicos. Procedimentos: [Mac](../PRIVATE_EXPORT.md), [Windows](../WINDOWS_TESTING.md), [menu](../PLAYER_MENU_PLAN.md).

## Backlog e encerramento

Cada issue tem critério de aceitação; fechar como concluída significa atender esse critério, não finalizar a campanha. Não fechar uma tarefa de “teste Windows” com evidência de build no Mac. Estados/labels e fórmula estão em [BACKLOG.md](../BACKLOG.md).

`python3 scripts/update_backlog.py --check` confere os resumos. Para ampliar escopo, cadastrar a issue em `docs/backlog.json`; não editar o bloco gerado do README manualmente. O token do Actions não acessa campos do Project: mudanças visuais de coluna não substituem estado/label da issue.

No relatório final, incluir mudança e motivo, testes executados com resultado, artefatos locais úteis, riscos/limites e próxima ação. Marcar explicitamente o que não foi executado. Manter atualizados os documentos afetados em vez de criar diários duplicados ou adicionar requisitos genéricos a todas as skills.
