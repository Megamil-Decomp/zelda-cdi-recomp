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
