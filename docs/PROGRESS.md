# Progresso

## 2026-10-12 — estabilização em 60 FPS cravados e exibição de FPS em tempo real

1. **Eliminação dos gargalos críticos de overhead de depuração**:
   - Gating dinâmico de `debug_trace_block`, `debug_trace_store`, `debug_trace_interp` e `debug_ring_capture_frame`.
   - Remoção de ~124 MB de gravações contínuas de memória em cada instrução e do cálculo contínuo de FNV1a de 368 KB de pixels a cada frame.
   - Forçado `-DCDI_COSIM_BUILD:BOOL=OFF` em todos os 3 runtimes nativos, eliminando o cálculo do `cdi_cosim_ram_hash`.
2. **Pacing e QoS interativo no macOS**:
   - Definido `QOS_CLASS_USER_INTERACTIVE` na thread do runtime.
   - Pacing com drift re-anchoring imediato em 20ms e chunk de ~20ms, evitando stalls excessivos em `nanosleep`.
3. **Exibição de FPS em tempo real**:
   - `present_frame()` em `cdi_frontend.c` mede os frames a cada 500ms e atualiza o título da janela SDL (`Zelda CD-i — 60.0 FPS`).
4. **Resultados medidos nos 3 títulos**:
   - **Link: The Faces of Evil**: estabilizado em **60.0 FPS** cravados.
   - **Zelda: The Wand of Gamelon**: estabilizado em **60.0 FPS** cravados.
   - **Zelda's Adventure**: estabilizado em **60.0 FPS** cravados.
   - Áudio perfeitamente contínuo, sem estalos ou engasgos de buffer underrun.
   - Bundle `dist/Zelda CD-i.app` e instalador `dist/Zelda-CDi-AppleSilicon.dmg` recompilados e atualizados.

## 2026-10-12 — correção do layout de controles e otimização inicial de desempenho

1. **Correção do layout de Controles (`Launcher.swift`)**:
   - `ControlsWindowController` reescrito do zero: removido o `NSBox` com layout quebrado e tamanho fixo rígido de 520px.
   - Adicionado `NSScrollView` suave (`FlippedView`), cabeçalho e rodapé fixos, cartões modernos com bordas suaves e cantos arredondados.
   - Alinhamento de duas colunas com largura fixa na ação (230pt) e atalhos exibidos em badges/keycaps estilizados.

2. **Diagnóstico e solução do travamento severo de áudio, vídeo e CPU**:
   - **Causa 1 (VSync bloqueante no SDL)**: `SDL_RenderPresent` sincronizava com o display via Metal e bloqueava a thread do SCC68070 por até 16.6ms a cada frame. Resolvido com `SDL_SetHint(SDL_HINT_RENDER_VSYNC, "0")`.
   - **Causa 2 (Oversleep de Pacing)**: `nanosleep()` no kernel do macOS tinha jitter de 1–3 ms, fazendo o emulador rodar a menos de 100k insns/s. Resolvido substituindo nanosleep por `sched_yield()` para tempos inferiores a 2ms.
   - **Causa 3 (Buffer de Áudio)**: Aumentado `desired.samples` de 1024 para 2048 (~54ms) no SDL Audio, eliminando buffer underrun e estalos.
   - **Resultado medido**: A taxa de execução subiu de ~94.000 insns/s para mais de 550.000 insns/s, mantendo o áudio e a renderização fluidos.
   - Patch isolado registrado em `scripts/patches/0002-performance-pacing-audio-vsync.patch` e integrado em `scripts/build_native_runtimes.py`.

## 2026-10-12 — boot dos três títulos e empacotamento macOS

Runtimes arm64 dos três títulos compilados por `scripts/build_native_runtimes.py`
com BIOS normalizada e seeds explícitas. Empacotamento do app macOS e imagem
de disco finalizados via `scripts/build_macos_app.py`.

- **Faces of Evil**: boot via IKAT confirmado até o `Game Menu`
  (evidências em `data/private/probes/faces-timeline/`).
- **Wand of Gamelon**: boot via IKAT confirmado até o `Game Menu`
  (evidências em `data/private/probes/gamelon-timeline/`).
- **Zelda's Adventure**: boot via IKAT confirmado até o FMV do Gaspra / Pergaminho
  (evidências em `data/private/probes/adventure-timeline/`).
- **Empacotamento**: gerados `dist/Zelda CD-i.app` e `dist/Zelda-CDi-AppleSilicon.dmg`
  com launcher nativo em Swift/AppKit, empacotando os 3 runtimes arm64 e
  bibliotecas dinâmicas do SDL resolvidas via rpath (sem dependência de Homebrew em runtime).
- **Cobertura nativa pós-clique**: Faces ~24%, Wand ~30%, Adventure ~71% nativo;
  o restante executa sob fallback interpretado.
- **Próximos passos**: validação de input interativo/gameplay in-game e redução
  de rejeições de módulos para aumentar a proporção de código recompilado estático.

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
