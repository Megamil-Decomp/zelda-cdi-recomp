# Investigação com REA

Este fluxo começou no piloto de Faces em 27/10/2026 e foi aplicado também a Gamelon/Adventure. REA é ferramenta de análise; a emissão continua com CdiRecomp e a execução combina recompilação estática e fallback interpretado. Para retomar, começar pelo [handoff](AI_HANDOFF.md) e pela [rota resumida REA](wiki/REA.md). Catálogo aceito e registros recentes prevalecem sobre exemplos históricos de candidatos nesta página.

## Ambiente isolado

`python3 scripts/run_rea.py ...` usa `build/rea-tools/toolchain.json`. O piloto fixou REA 6.8.0, Node 24.22.1 e Ghidra 12.1.4, com JDK 25 já instalado. O decompilador do Ghidra foi compilado para arm64. Não houve registro de MCP nem alteração de configuração global do agente. Arquivos de versão, origem e integridade estão em `data/private/rea-pilot/`; as ferramentas ficam em `build/rea-tools/`.

O Ghidra 12.2 foi recusado pelo controle de versão do REA; não remover esse controle. Instalação em outra máquina exige obter as ferramentas oficiais e configurar seus caminhos locais. As ferramentas autorais não fazem download durante os testes.

## Preparar um módulo

```sh
python3 scripts/prepare_rea_module.py \
  --module data/private/caminho/modulo-original.bin \
  --targets data/private/caminho/report.json \
  --output data/private/rea-pilot/nova-preparacao
```

Também é possível usar `--cue`, `--lba` e `--size` com uma extensão Form 1 contígua explicitamente verificada no inventário privado. Isso não é um extrator geral de filesystem. Tamanho, cabeçalho OS-9/Prog, paridade, CRC e entradas são validados; Form 2, mudança de arquivo/canal e EOF antecipado são rejeitados.

O adaptador preserva o módulo completo em `module.bin`. `analysis.bin` acrescenta um salto sintético e padding antes dele. Endereço de análise menos `0x100` corresponde ao offset do módulo. O envelope não reloca literais absolutos nem modela hardware/ABI OS-9; jamais usá-lo no runtime.

## Executar a análise automática

```sh
python3 scripts/analyze_rea_module.py \
  data/private/rea-pilot/nova-preparacao \
  --targets data/private/caminho/report.json \
  --hotspots 3 \
  --output data/private/rea-pilot/nova-analise
```

O comando reconfere os bytes, verifica o mapeamento com REA/Ghidra, analisa a entrada do módulo e inspeciona um número limitado dos destinos observados mais frequentes. Preserva Evidence completo, stderr e resumo privado. Confere operação, provider e identidade do artefato nas respostas; falhas não disparam tentativas idênticas. Diretórios existentes não são sobrescritos.

`seeds.tsv` identifica **código observado**, sem presumir fronteiras de função. Uma captura completa pode gerar `unvalidated-module.seeds` como entrada experimental para o recompilador. Esse arquivo não é aplicado automaticamente. O Ghidra usa um superset 68040; um resultado estático não comprova legalidade SCC68070, execução ou equivalência do pseudocódigo.

## Gate para recompilação

1. Exigir ledger completo, sem overflow, pausado de forma estável e com SHA-256 integral correspondente ao módulo. O probe informa completude e preserva evidência parcial quando uma página falha.
2. Executar CdiRecomp com `--module-seeds` e saída nova em `build/`. Manter todos os diagnósticos estritos e falloff; não remover erros para forçar emissão.
3. Compilar runtime candidato separado, com fontes e termos auditados. O patch 0007 evita uma inferência de tabela dentro da própria instrução JMP; não substitui o destino calculado nem remove fallback.
4. Comparar cenário, eventos de entrada, frames, contadores nativos/interpretados e falhas. As razões incluem BIOS; diferenças de clique exigem registrar o alinhamento. Correspondência visual isolada não certifica CPU ou áudio.
5. Manter candidato experimental até validar além de introdução/menu. Não substituir o aplicativo entregue com base apenas no percentual nativo.

O harness e os comandos específicos da mídia desta máquina estão em `data/private/rea-pilot/compare_runtimes.py` e nos relatórios privados. Usa bateria própria, SDL dummy, parada por frame e histórico paginado. Seus hashes, caminhos, eventos e detalhes derivados permanecem privados.

## Abrir o candidato desta máquina

```sh
python3 scripts/run_faces_rea_candidate.py --check
python3 scripts/run_faces_rea_candidate.py
```

O primeiro comando apenas confere identidades. O segundo abre o candidato experimental de Faces a 1x, com configuração/bateria separadas em `data/private/rea-pilot/interactive-player/` e log novo por sessão. Não substitui o launcher nem usa os saves do aplicativo normal. Requer os artefatos privados do piloto; não é distribuição portátil e não contém certificação de campanha/áudio. A advertência de mínimo macOS da SDL ocorreu nos binários antigos do piloto; a entrega Mac 0.1.7 usa SDL2 privado compilado com mínimo 13. Conferir qual runtime está sendo executado, sem transferir a aceitação do pacote atual ao piloto histórico.

Após a investigação da regressão, o manifesto privado seleciona `irq-fixed`, build com os patches 0008 de fetch e 0009 de prioridade de IRQ. Ela passou pelo replay CMake de ataques e avanço à direita na primeira área e pelo ensaio de abertura a 1x. São trechos curtos, não certificação de campanha; a identidade do objeto específico descrito pelo usuário continua uma limitação. Ver `FACES_GAMEPLAY_REGRESSION_PLAN.md` e o progresso de 28/10.

Cada execução gera também `session-*.json`, com comando, identidade do runtime e status/sinal de saída. `--candidate menu` seleciona o candidato anterior à investigação; `--candidate fetch-fixed` preserva a versão que contém apenas a correção de fetch, para comparação. Nenhuma dessas escolhas substitui o pacote normal ou a bateria do usuário.

## Testes

```sh
python3 -m unittest discover -s tests -v
```

As fixtures são autorais e sintéticas. A regressão do gerador exige o checkout upstream auditado e `cc`; sem eles é marcada como indisponível. Ela compara original/corrigido sem alterar o upstream, reproduz a falha de interpretação de extensão e mantém uma tabela externa legítima funcionando. A suíte não exige BIOS/discos.

Fontes: [REA](https://github.com/morluto/rea), [raw m68k](https://github.com/morluto/rea/blob/main/docs/raw-binary.md), [Ghidra](https://github.com/NationalSecurityAgency/ghidra). O isolamento não altera os termos do cdirecomp/core, registrados em `UPSTREAM_AUDIT.md`.

## Adventure, Gamelon e o launcher

O plano de ampliação está em `REA_OTHER_TITLES_PLAN.md`. As provas iniciais de Adventure/Gamelon usam o Prog principal; o Subr de Adventure continua excluído. Não reutilizar seeds entre títulos: mesmo nome de módulo não significa mesma identidade. Coletar o ledger completo, preparar novo envelope com `--targets`, investigar no REA e só então comparar o candidato emitido estritamente com a referência.

Para empacotar candidatos já verificados, `build_macos_app.py --runtime-catalog` recebe JSON privado com `schema_version: 1` e `runtimes` contendo exatamente `faces`, `gamelon` e `adventure`. Cada entrada exige `path`, `sha256` completo e pode ter `status_text`. O path deve resolver dentro de `build/`, `dist/` ou `data/private/` do projeto. O arquivo copiado é conferido novamente antes de ajustar bibliotecas/assinar; o manifesto registra separadamente o hash de origem e o hash final do binário empacotado.

Exemplo local, dependente dos artefatos privados já produzidos:

```sh
python3 scripts/build_macos_app.py --output dist/rea \
  --runtime-catalog data/private/rea-titles/runtime-catalog.json \
  --text-mod 'dist/ptbr-menu/Zelda CD-i.app/Contents/Resources/adventure-ptbr.txt' \
  --menu-mod 'dist/ptbr-menu/Zelda CD-i.app/Contents/Resources/adventure-menu-ptbr.txt'
```

O exemplo foi usado na entrega 0.1.5; o catálogo é mutável e hoje deve ser conferido contra o manifesto da entrega selecionada, sem inferir versão pelo nome. A seleção não certifica campanha. Ensaios, imagens, seeds e proveniência detalhada ficam em `data/private/rea-titles/`; os testes sintéticos do catálogo não dependem de mídia comercial.
