---
name: zeldas-cdi-rea
description: "Preparar módulos OS-9 do Zelda CD-i para REA/Ghidra, conferir Evidence e propor seeds observadas para emissão estática. Usar ao investigar cobertura ou destinos; não é fluxo de tradução, runtime ou decompilação geral de aplicativos."
---

# REA para Zelda CD-i

Ler [AGENTS](../../../AGENTS.md), [handoff](../../../docs/AI_HANDOFF.md) e a [rota REA](../../../docs/wiki/REA.md). Usar `scripts/run_rea.py` com o toolchain privado conferido; não presumir MCP registrado ou ferramentas globais. As versões históricas compatíveis e as chaves do JSON estão nessa rota.

1. Identificar módulo/revisão e cenário autorizados. Conferir módulo completo, cabeçalho/paridade/CRC, SHA-256 e ledger paginado estável sem overflow. Nome de módulo não identifica seus bytes.
2. Preparar com `prepare_rea_module.py`, preservando mídia e escolhendo saída nova sob `data/private/rea-pilot/` ou `build/`, como exige o validador. `analysis.bin` contém prefixo sintético: subtrair **0x100** para obter offset do módulo; não confundir com endereço guest em RAM e nunca usar o envelope no runtime.
3. Executar `analyze_rea_module.py` com hotspots limitados. Conferir operação/provider/digest/estado no Evidence e preservar JSON/stderr. Falha pede diagnóstico antes de outra tentativa, não relaxamento de gates.
4. Interpretar `seeds.tsv` como código observado. Ghidra usa superset 68040, sem provar ISA SCC68070, ABI OS-9 ou fronteiras de função. `unvalidated-module.seeds` não está aceito para runtime só porque a análise terminou.
5. Propor emissão estrita por **CdiRecomp** em candidato separado, seguida de comparação e 1x pelo [fluxo de validação](../zeldas-cdi-validation/SKILL.md). Subr de Adventure continua sem layout comprovado; não reaproveitar o layout de Hotel Mario.

Os comandos já mantidos estão em [REA_WORKFLOW.md](../../../docs/REA_WORKFLOW.md); conferir `--help` da versão instalada antes de acrescentar flags. Não reimplementar os validadores existentes, regenerar todos os jogos sem motivo ou promover catálogo/app nesta etapa de análise. Seeds reais, binários e Evidence permanecem privados; a saída pública é um resumo das conclusões e limites.
