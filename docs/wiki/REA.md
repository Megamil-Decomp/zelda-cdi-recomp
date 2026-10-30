# REA no Zelda CD-i

Fluxo específico do projeto, não um manual geral de engenharia reversa. O procedimento completo existente está em [REA_WORKFLOW.md](../REA_WORKFLOW.md); esta página explica as decisões e a retomada. REA analisa; **CdiRecomp emite** e o runtime executa com fallback medido.

## Ambiente e primeiro diagnóstico

O ambiente privado verificado usa **REA 6.8.0**, Node **24.22.1**, Ghidra **12.1.4**, JDK **25** e decompilador Ghidra compilado para arm64. São versões do piloto, não uma recomendação de versões atuais. O controle REA rejeitou Ghidra 12.2; não removê-lo para contornar incompatibilidade.

`scripts/run_rea.py` lê `build/rea-tools/toolchain.json`. Em outra máquina, preparar ferramentas de origem oficial com versões compatíveis e preencher os caminhos absolutos reais:

| Chave obrigatória | Deve apontar para |
| --- | --- |
| `node` | Executável Node da instalação selecionada |
| `rea` | `scripts/rea.mjs` do pacote instalado `rea-agents` |
| `ghidra` | Diretório da distribuição Ghidra compatível |
| `java_home` | Diretório HOME do JDK usado pelo Ghidra |

Conferir os arquivos e a versão instalada; não copiar o JSON de outra máquina sem ajustar os paths. A instalação e seus hashes ficam privados. O wrapper configura PATH, GHIDRA_INSTALL_DIR, JAVA_HOME e TMPDIR apenas no subprocesso, sem registrar MCP ou editar configuração global.

```sh
python3 scripts/run_rea.py --help
python3 scripts/prepare_rea_module.py --help
python3 scripts/analyze_rea_module.py --help
```

Se faltar o toolchain, o wrapper termina com diagnóstico. Isso não significa que o runtime do jogo precise do REA no computador destino. Um clone público ainda pode executar as fixtures sintéticas de preparação/Evidence.

## Entrada correta

Usar módulo **OS-9 Prog / 68000 completo**, obtido da mídia local autorizada, com tamanho, paridade, CRC e identidade conferidos. O preparador não aceita qualquer blob e não é extrator geral de filesystem. A alternativa CUE exige extensão Form 1 contígua explicitamente verificada (`--cue`, `--lba`, `--size`); não inferir setores contíguos de um arquivo intercalado.

As saídas do preparador/analisador devem ser diretórios **novos sob `data/private/rea-pilot/` ou `build/`**. Estar em outra pasta privada não satisfaz o validador. Não sobrescrever uma preparação existente.

Obter destinos observados pelo [probe](Validation.md) no cenário relevante. Exigir ledger completo, sem overflow, estável durante paginação e associado ao SHA-256 integral correto. `dropped=0` sozinho não demonstra que todas as páginas foram capturadas. Nome de módulo igual não permite reaproveitar seeds entre títulos/revisões.

Exemplo de formato de comando — substituir os nomes genéricos por arquivos privados existentes e escolher diretórios de saída novos:

```sh
python3 scripts/prepare_rea_module.py \
  --module data/private/rea-pilot/investigacao/modulo.bin \
  --targets data/private/rea-pilot/investigacao/targets.json \
  --output data/private/rea-pilot/investigacao/preparado

python3 scripts/analyze_rea_module.py \
  data/private/rea-pilot/investigacao/preparado \
  --targets data/private/rea-pilot/investigacao/targets.json \
  --hotspots 3 \
  --output data/private/rea-pilot/investigacao/analise
```

## Ler o resultado sem promover uma hipótese

- `module.bin` preserva os bytes completos. `analysis.bin` acrescenta salto/padding sintéticos de **0x100** bytes: endereço da análise menos 0x100 dá offset do módulo. Não misturar esse endereço com a base guest carregada em RAM. O envelope não reloca literais absolutos e nunca entra no runtime.
- `seeds.tsv` marca **código observado**, não fronteiras comprovadas de funções. O Ghidra usa um superset 68040; decodificação/pseudocódigo não prova legalidade SCC68070 nem ABI OS-9 correta.
- O analisador verifica envelope/identidade antes de chamar REA, depois verifica Evidence: operação, provider `ghidra`, arquitetura, digest do artefato e estado de mapeamento. Preservar JSON/stderr completos, não apenas a narrativa gerada por uma IA.
- `procedure_completed=true` significa que a investigação estática terminou. `unvalidated-module.seeds` é entrada **experimental**; `candidate_seeds_validated_for_runtime=false` permanece falso até outro processo de emissão/validação. Captura parcial não deve gerar esse arquivo para o emissor.

## Gate de emissão e aceitação

Esta rota de preparação cobre o perfil Prog/68000 suportado. ROM inteira, módulos de outro tipo e Subr não passam a ser suportados por mudar seu cabeçalho ou CRC. Para BIOS, o emissor é `CdiRecompBios`, com arquivo `--seeds` próprio; conferir formato/endereço na revisão auditada. Ele mostra usage sem argumentos, mas não possui o mesmo tratamento `--help` de `CdiRecomp`. Não passar automaticamente offsets do envelope ou `unvalidated-module.seeds` do módulo para o emissor de BIOS.

Conferir `CdiRecomp --help` da revisão auditada antes de usar `--module-seeds`; manter saída nova em `build/`, diagnóstico estrito de instruções/fall-through e o layout de exports comprovado do módulo. **Não** aplicar o layout específico de Hotel Mario ao Subr de Adventure: ele continua excluído, sem layout estabelecido.

Compilar candidato separado e comparar com a referência usando mesmos inputs/estado, medição por intervalo e ensaio a 1x. Registrar código/BIOS incluídos, falhas, transições, áudio e limites. Não aceitar por FPS, tela de título, demo automática ou maior razão nativa. Só depois considerar promoção por catálogo de identidades. Ver [desenvolvimento](Development.md) e [validação](Validation.md).

Se uma operação REA falhar, guardar Evidence/erro, diagnosticar entrada/provider/versão e reduzir a pergunta. Não repetir a mesma operação inalterada nem desativar gates. As ferramentas existentes já limitam hotspots/tempo e recusam sobrescrever diretórios.

Fontes das ferramentas: [REA](https://github.com/morluto/rea), [Ghidra](https://github.com/NationalSecurityAgency/ghidra). As licenças dessas ferramentas não substituem os [termos do runtime/core](../UPSTREAM_AUDIT.md).
