# Progresso

## 2026-10-12 — primeiro boot de Faces até o menu

Git local criado (commit inicial `f870f74`, sem mídia/derivados). Runtimes arm64
dos três títulos compilados por `scripts/build_native_runtimes.py` com a BIOS
normalizada (swap16) e seeds explícitas. Detalhes em `RUNTIME_ACCEPTANCE.md`.

- Shell do player: Faces e Wand chegam a `Play CD-i` com cursor ativo.
- Faces: clique normal via IKAT inicia o disco; logos, título e `Game Menu`
  observados em capturas privadas (`data/private/probes/faces-timeline/`).
- Após o clique, a execução do jogo é majoritariamente interpretada
  (~26% nativo no intervalo pós-clique, incluindo BIOS); há 2 rejeições de identidade de
  módulo. Não apresentar como recompilação completa.
- Velocidade aparente ~20,5 quadros/s em `pace=1`; causa não isolada.
- Não testados: gameplay de Faces, carregamento de Wand e Zelda's Adventure,
  pacote `.app`/`.dmg`.

## 2026-10-12 — M0 concluído

O diretório inicial continha somente briefing no README, três pares BIN/CUE e três BIOS. O checkout upstream mencionado no briefing não existia e foi obtido para auditoria. O briefing original foi preservado em `PROJECT_BRIEF.md`; o README agora é a entrada de uso do projeto.

### Evidências executadas

| Verificação | Resultado | Evidência local |
| --- | --- | --- |
| Diagnóstico do host | macOS arm64; Clang/CMake/SDL disponíveis; exit 0 | `data/private/environment.json`, `ENVIRONMENT.md` |
| Build frontend upstream | Executáveis Mach-O arm64; exit 0 | `build/upstream-audit/logs/recompiler-build.log` |
| CTest frontend | 6/6 passaram; exit 0 | `recompiler-ctest.log` no mesmo diretório |
| Componentes runtime | Build exit 0; 11/11 CTest passaram | `runner-components-build.log`, `runner-ctest.log` |
| Fixture adicional de aliases | Passou; exit 0 | `function-aliases.log` |
| Executável completo do player | Build exit 2 no link; faltam 3 funções da BIOS gerada | `runner-full-build.log`; falha preservada sem stubs |
| Ferramenta própria | 20 testes sintéticos passaram; repetidos na revisão final | `python3 -m unittest discover -s tests -v` |
| Verificação de mídia | 9 arquivos, 3 discos, 35 amostras por volume; exit 0 com avisos | `data/private/media-report.json`, `media-verification.log` |
| Lock local | Criado sem sobrescrever anterior; comparação exit 0 | `data/private/media-lock.json`, `media-comparison-report.json`, `media-comparison.log` |
| Inventário OS-9 sem emissão | Três exit 0; Faces 5, Wand 5, Adventure 4 módulos; CRC/paridade válidos nos encontrados | `data/private/inventory-*.log` |
| Exclusões de Git | 9 caminhos privados ignorados e 5 caminhos de fontes permitidos em repositório temporário | Sem incluir mídia em índice e sem inicializar Git no projeto principal |
| Preservação upstream | `git status --short` vazio no clone e no core após builds/testes | Commit e submódulo em `UPSTREAM_AUDIT.md` |

Os seis testes CTest do frontend, onze do runtime, uma fixture Python upstream e vinte testes Python próprios totalizam 38 verificações reportadas; não equivalem a 38 cenários de gameplay.

Os comandos do inventário, depois dos testes sem mídia:

```sh
build/upstream-audit/recompiler/CdiRecomp \
  "roms/Link The Faces of Evil/Link - The Faces of Evil (Europe).cue" \
  > data/private/inventory-faces.log 2>&1
build/upstream-audit/recompiler/CdiRecomp \
  "roms/Zelda The Wand of Gamelon/Zelda - The Wand of Gamelon (Europe).cue" \
  > data/private/inventory-gamelon.log 2>&1
build/upstream-audit/recompiler/CdiRecomp \
  "roms/Zeldas Adventure/Zelda's Adventure (Europe).cue" \
  > data/private/inventory-adventure.log 2>&1
```

### Achados e limites

- Frontend e componentes sintéticos funcionam neste Mac. A execução integrada continua não testada; nenhum Zelda nem BIOS foi iniciado.
- Os textos de licença principal/core diferem da PolyForm oficial. Usar o upstream como referência experimental isolada; esclarecer termos antes de distribuição. As alegações upstream de autoria/proveniência não foram certificadas de forma independente.
- Faces e Wand contêm setores fora do volume declarado, incluindo pequena cauda uniforme. A ferramenta informa avisos; não estabelece sua origem, integridade ou necessidade para o jogo.
- Hashes são observados e servem ao lock pessoal. Não há autenticação externa dos dumps, validação completa EDC/ECC ou certificação de todos os recursos.
- Os formatos de textos, fontes e cinematics continuam não identificados por título. `LOCALIZATION.md` é proposta, não tradução ou suporte implementado.
- Não houve alterações nos arquivos de mídia, geração de BIOS/jogo, mudanças versionadas no upstream, commits ou pushes.

### Próximo trabalho

M1 de Faces: mapear entradas de módulos, referências inicializadas e destinos indiretos; definir uma comparação pequena antes da primeira emissão privada. Integrar BIOS/player e medir dispatch nativo em marcos seguintes. Critérios de FOE-BOOT-001, roadmap e instrução pronta estão em `ROADMAP.md`.
