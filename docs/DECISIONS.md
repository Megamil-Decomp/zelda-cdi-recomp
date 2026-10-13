# Decisões

## 2026-10-12 — começar por uma prova pequena em Faces

Seguir o briefing preservado: foco inicial em Faces of Evil, com Wand of Gamelon e Zelda's Adventure em marcos posteriores. Nesta execução, concluir apenas M0. Não implementar uma engine substituta ou tradução antes de validar execução.

## 2026-10-12 — upstream isolado como referência experimental

Manter `upstream-cdirecomp/` fora do repositório principal, sem mudanças em arquivos versionados. Usar seus testes e frontend para avaliar a plataforma. O código e o núcleo m68k têm arquivos intitulados PolyForm Noncommercial, mas o texto local difere do padrão oficial; tratá-los como termos específicos do upstream, sem presumir compatibilidade com um projeto permissivo ou comercial. A comparação completa e as diferenças estão em `UPSTREAM_AUDIT.md`.

Recomendação técnica de curto prazo: dependência experimental separada para a prova não comercial, com commit fixo, em vez de começar do zero antes de verificar o que já funciona. Isso não resolve licenciamento por isolamento. Uma licença alternativa/fork autorizado ou uma implementação própria são caminhos distintos para publicação com outros termos; nenhuma negociação ou contribuição foi enviada.

## 2026-10-12 — mídia intacta e resultados privados

Preservar os caminhos originais `roms/` e `bios/`, sem copiar mídia para o upstream. Builds em `build/`; hashes e inventários em `data/private/`. `.gitignore` inclui esses caminhos e o checkout upstream. Nenhum repositório principal/commit/push criado nesta fase.

## 2026-10-12 — fidelidade e medição antes de melhorias

Propor execução do kernel OS-9 recompilado e modelos de hardware como primeira referência. Código em RAM precisa de identidade, relocação, invalidação e cobertura. Fallback interpretado só serve à pesquisa e não comprova recompilação do jogo.

## 2026-10-12 — PT-BR como mod externo posterior

Planejar traduções autorais externas e opcionais, com desativação em tempo de execução, mantendo recursos originais. Investigar textos, fontes, imagens e codecs antes de selecionar hooks. Implementação adiada para depois da execução validada, conforme o briefing.

## 2026-10-12 — Otimização de desempenho (VSync, áudio e pacing) e tela de controles

1. **Desacoplamento de VSync**: Por padrão no macOS/Metal, `SDL_RenderPresent` bloqueava a thread de execução do SCC68070 por até 16.6ms a cada frame. Com `SDL_SetHint(SDL_HINT_RENDER_VSYNC, "0")`, a apresentação para GPU é assíncrona, desimpedindo o avanço do clock do CD-i.
2. **Buffer de áudio SDL**: Aumentado de 1024 para 2048 amostras (~54 ms a 37.8 kHz), evitando underrun e estalos de áudio no CoreAudio causados por pequenos descompassos de tempo.
3. **Pacing preciso no macOS**: Substituído o loop cego de `nanosleep()` com jitter de 1–3 ms no Mach kernel por um limiar de 2 ms com `sched_yield()`, aumentando a cadência de instruções de ~94k insns/s para mais de 550k insns/s com frames ativos.
4. **Layout de Controles**: `ControlsWindowController` refatorado com `NSScrollView`, cartões modernos de cantos arredondados, alinhamento fixo de colunas e badges visuais de atalhos ("keycaps").

## 2026-10-12 — Desativação de overhead de debug/co-simulação e contador de FPS em tempo real

1. **Gate dinâmico para anéis de depuração**: O upstream alocava ~124 MB de ring buffers (`s_trace_ring` de 92MB e `s_store_ring` de 32MB) e gravava neles a cada instrução e a cada escrita de memória, além de calcular hashes de tela (`mcd212_video_frame_hash`) de centenas de kilobytes a cada frame e executar pesquisas lineares em tabelas hash (`debug_trace_interp`). Em modo de jogador comum (sem `--hold`, `--stop-seq` ou conexão TCP ativa), essas rotinas foram desativadas através de `s_debug_tracing_active`, preservando apenas o safepoint de interrupções (`recomp_pending_irq_mask`).
2. **Pacing com QoS interativo e tolerância de drift**: No macOS arm64, o thread principal do runtime agora recebe `QOS_CLASS_USER_INTERACTIVE`. O limiar de reancoragem de deadline (`s_pace_deadline`) foi reduzido para 20ms e o chunk de ciclos foi ajustado para 1 quadro (~20ms), eliminando paradas excessivas em `nanosleep()` e impedindo acúmulo de lag.
3. **Contador de FPS em tempo real**: Em `cdi_frontend.c`, `present_frame()` calcula dinamicamente a taxa de quadros e atualiza o título da janela SDL para `Zelda CD-i — XX.X FPS` a cada 500ms, proporcionando visibilidade clara da fluidez aos jogadores sem overhead visual no framebuffer do CD-i.
4. **Desativação obrigatória de `CDI_COSIM_BUILD`**: Forçado `-DCDI_COSIM_BUILD:BOOL=OFF` com purga automática de caches anteriores em `build_native_runtimes.py`, evitando o cálculo contínuo de `cdi_cosim_ram_hash` que consumia quase metade da CPU.

## 2026-10-12 — Prevenção de fechamentos acidentais e suporte IKAT Canal C para Zelda's Adventure

1. **Não-fatalidade na captura de mouse e troca de foco**: No upstream, `apply_mouse_capture()` retornava `0` se o SO negasse a captura ou ao ocorrer transição de foco (`SDL_WINDOWEVENT_FOCUS_LOST`/`GAINED`), e o loop em `cdi_frontend_pump()` executava `if (!apply_mouse_capture()) return 0;`, matando imediatamente o jogo. Foi ajustado para ignorar erros de captura sem encerrar o processo, e o evento de foco apenas chama `apply_mouse_capture()` de forma não-bloqueante.
2. **Proteção contra saída involuntária pela tecla ESC**: A tecla ESC pura encerrava o processo instantaneamente sem confirmação. O encerramento por teclado agora exige atalho com modificador (`Cmd+Q` ou `Cmd+Esc`).
3. **Fallback IKAT Canal C (`slave.c`) para Zelda's Adventure**: Ao caminhar para novas telas, *Zelda's Adventure* realiza consultas de status de drive e TOC através do Canal C do microcontrolador IKAT (`0xF2` status de erro do mecanismo, `0xF1` bandeja, `0xF9`, `0x8x` configs). O upstream descartava esses comandos silenciosamente (`[ikat] unmodeled channel-C command dropped`), o que deixava o driver do CD-RTOS aguardando resposta em loop até disparar timeout de I/O e a mensagem *"O CD foi retirado ou pode estar sujo"*. Foi implementado o envio da confirmação padrão do IKAT (`{ 0xA5, cmd, 0x00 }`) via `publish_and_interrupt(CHANNEL_C, ...)`, eliminando o timeout e permitindo transições normais de tela no jogo.
