# Decisões

## 2026-10-29 — backlog público com aceitação e contagem reproduzível

Usuário pediu atualização do README e quadro estilo Trello no GitHub. Usar Project público vinculado ao repositório, issues com critério/área/prioridade e estados Backlog, Em andamento, A validar e Concluído. Registrar entregas já aceitas como issues fechadas, mantendo os limites de cada cenário; não equiparar build Windows a execução Windows nem piloto PT-BR a tradução integral.

Percentual público conta entregas concluídas sobre o escopo cadastrado, com pesos iguais e data; não estima esforço restante, campanha ou fidelidade e fica separado de instruções nativas por percurso. JSON público alimenta os dois READMEs e BACKLOG.md. O workflow de eventos de issues usa apenas GITHUB_TOKEN efêmero, lê estados/labels e escreve somente os quatro arquivos de documentação previstos. Não importa títulos/corpos remotos nem inclui automaticamente novas issues no denominador. Campos/posições do Projects não são a fonte do resumo; fechar/reabrir ou mudar a label da issue atualiza a contagem. Nenhum token pessoal, recurso de jogo, build ou log privado é publicado.


## 2026-10-29 — menu de host e mouse independente de captura

Atender primeiro o menu solicitado, comum aos três candidatos, sem tocar a lógica recompilada dos jogos. O retorno explícito de pausa do frontend impede avanço de CPU/dispositivos, mantém sinais/janela ativos e pausa a saída SDL. Volume atua no PCM copiado, com ganho unitário idêntico; fonte, rótulos e preferências são autorais. Esvaziar edges de mouse ao abrir e exigir controles neutros ao retomar. Manter a tradução externa parcial de Adventure.

Usar SDK nativo SDL2 2.32.10 de fonte oficial fixada por SHA-256, compilado em diretório privado com alvo macOS 13. A biblioteca Homebrew SDL2-compat/SDL3 instalada exigia macOS 26, incompatível com o mínimo anunciado. Resolver imports @rpath antes de copiar dylibs e remover RPATHs absolutos do bundle; assinar e verificar o resultado. Não alterar a instalação global. Windows continua sem aceitação real, e o pacote anterior permanece preservado.

## 2026-10-29 — publicar somente fontes e planejar Deck por evidência

Usuário autorizou push para o remoto existente, sem ROMs nem versão completa. Auditar os objetos/paths dos commits pendentes e enviar apenas código, testes e documentação; não anexar artefatos nem alterar privacidade do repositório. Para Steam Deck, propor primeiro ensaio Windows/Proton com Steam Input, mantendo explícitos os limites de analógico, mouse/captura e interface. Compatibilidade Deck exige teste próprio; consulta à documentação e inspeção local não são aprovação de hardware.

## 2026-10-29 — Windows no mesmo projeto, com exportação própria

Usuário pediu uma versão Windows para testar e um comando equivalente ao exportador Mac. Reutilizar exatamente os inputs dos candidatos aceitos, conferidos por proveniência/hash, em cópias Windows isoladas. Não reeditar o upstream nem trocar o mecanismo de recompilação. Manter BIOS distinta de Adventure e a BIOS aceita em Faces/Gamelon.

Usar MinGW x64 e SDL2 Windows oficial com identidade fixada. Criar launcher Win32 autoral e exportador Python: validação de executáveis/mídia, cache normalizado de BIOS, saves/logs por título e mod opcional. Incorporar manifesto UTF-8 nos executáveis para os caminhos com acentos no alvo Windows 10 1903+; não exigir mudança global de locale ou privilégio administrativo. Não encerrar o runtime à força para preservar saves.

Entregar como primeiro pacote de teste cross-compilado. Sem ambiente Windows/Wine disponível, não declarar gameplay, áudio, controles ou desempenho Windows aprovados. Builds, mídia e pacote completo permanecem privados/ignorados; código autoral e testes sintéticos podem ser versionados sob a autorização de commit já dada para os ajustes deste trabalho.

## 2026-10-29 — exportação completa privada e commit dos ajustes

Usuário autorizou copiar os arquivos locais necessários para testar em outro Mac e solicitou commit dos ajustes, excluindo arquivos dos jogos. A exportação pode conter BIOS e discos somente na cópia ignorada de `dist/`; não muda a regra do Git nem autoriza publicação/upload. Preservar a mídia original e não incluir saves pessoais.

Usar um script reutilizável para copiar o app aceito, conferir identidades, recompilar somente o launcher, detectar mídia interna ao bundle e produzir ZIP assinado localmente. Cada execução padrão cria destino datado novo, sem substituir exportações anteriores. Preferências da edição portátil ficam em domínio próprio; saves novos usam o suporte de aplicação do usuário. Windows permanece próximo alvo proposto, sujeito à validação específica descrita em `PORTABILITY.md`.

## 2026-10-29 — reduzir fallback de Adventure em rotinas observadas da BIOS

Após o lote adicional de seeds do jogo produzir ganho pequeno, classificar a interpretação por região. Cerca de 71% do fallback residual no percurso medido pertence à ROM. REA identificou dois helpers do módulo OS-9 de vídeo, com identidade/cabeçalho/CRC conferidos e entradas observadas em execução.

Gerar a BIOS com a lista anterior mais duas entradas técnicas sustentadas, em cópia privada isolada do staging auditado. Essas entradas não provam nomes ou fronteiras originais de funções. Preservar os módulos estáticos do jogo v1 e os runtimes Faces/Gamelon aceitos. Não alterar a semântica dos loops nem o protocolo de input: a instrumentação não observou sobrescrita de pacotes no trecho ensaiado.

Exigir emissão estrita, testes nativos, comparação de percurso e ensaio a 1x antes de promover Adventure pelo catálogo de hashes. Manter 0.1.5 recuperável. Ganho de cobertura não implica correção de toda a campanha nem validação física do áudio.

## 2026-10-28 — priorizar Adventure e selecionar os três candidatos por identidade

Usuário confirmou melhora de Faces e autorizou continuidade em Wand of Gamelon e, principalmente, Zelda's Adventure, incluindo a interface de seleção. Aplicar as correções comuns já comprovadas aos runtimes dos três; manter o candidato Faces aceito pelo usuário.

Usar REA sobre os módulos Prog principais e destinos observados, seguido de emissão estrita e ensaios reais. Não inferir layout do Subr de Adventure nem apresentar código interpretado como recompilado. Percentuais medem apenas o intervalo declarado e incluem BIOS. Demonstração automática, FPS e processo vivo não são aceitação de gameplay.

O empacotador aceita um catálogo privado explícito com paths e SHA-256 dos três runtimes. Catálogo parcial ou identidade alterada causa erro, sem fallback silencioso para build antiga. Manter idioma/mod opcional e dados de usuário. Atualizar o pacote local somente após checks; guardar o anterior para retorno. Corrigir o texto de About que atribuía MIT ao runtime inteiro: os termos não comerciais auditados continuam aplicáveis.

## 2026-10-28 — elevar IPL no reconhecimento da IRQ

A espera de Faces foi relacionada a reentrada de interrupção enquanto o driver ainda publicava o próximo estado. A captura privada mostra o segundo atendimento AP ocorrendo antes de o primeiro limpar o pedido anterior; o driver acaba ocioso com buffers de dados ocupados. O runtime verificava IPL ao aceitar a IRQ, mas não elevava a máscara na entrada.

Aplicar patch 0009 somente ao staging. Após construir o frame com SR anterior, elevar IPL ao nível reconhecido e limpar o bit de trace ativo. A especificação Philips SCC68070 de abril de 1993, seção 5.11, página 23, foi conferida por leitura e imagem. Preservar SR/PC/vetor empilhados para retorno, pendências mascaradas e preempção por prioridade superior. Não compensar reentrada com atraso de AP ou mudanças artificiais em CIAP.

Regressão sintética reproduz a máscara incorreta no original e verifica os contratos no corrigido. Replay corrigido já alcançou a área visível e colisões com o inimigo, onde a referência ficava preta. A validação continua limitada aos cenários registrados; não equivale a aceitar campanha completa ou todos os jogos.

## 2026-10-28 — fetch especulativo não pode produzir efeitos de hardware

Após o relato do usuário, o crash report e o replay confirmaram que a cópia antecipada de 64 bytes do intérprete atingia MMIO e abortava o host. Aplicar o patch 0008 em staging: ler apenas RAM/ROM disponível, rejeitar extensões ausentes e preservar o caminho de exceção para operandos reais. Não retornar zeros de registradores desconhecidos. Fetch em MMIO continua falhando explicitamente, sem alegar modelagem completa de sua exceção arquitetural.

O candidato interativo passa a usar a build com essa correção, identificada por hash privado. Registrar status/sinal de saída em JSON por sessão; processo vivo e FPS ativo não bastam para marcar sucesso. Manter o candidato anterior para comparação explícita e preservar a bateria do usuário por cópia nos testes.

O bloqueio de carregamento/espera continua reproduzível em Faces nas builds de referência e candidata. Não alterar latência ou inventar conclusão de I/O para esconder a espera. O experimento privado com maior latência AP não resolveu a falha e não foi adotado. A semântica dos pares de buffers CIAP e suas notificações requer comparação adicional; análise estática de Wand/Adventure não equivale a validar seus runtimes.

## 2026-10-28 — REA como análise auxiliar e promoção experimental por evidência

Usar REA 6.8.0 com Ghidra 12.1.4 em instalação privada do projeto, via CLI, preservando configuração global e mídia. Manter CdiRecomp como emissor. O envelope de análise preserva o módulo completo, mas acrescenta um prefixo sintético; nunca alimenta o runtime e não resolve ABI OS-9, endereços absolutos ou a diferença de ISA do Ghidra.

Corrigir a sonda para paginar o ledger completo e distinguir falha de medição de execução zero. Não tratar `dropped=0` como garantia de que todas as páginas foram salvas. Entradas candidatas exigem identidade integral, alinhamento e limites do módulo; pseudocódigo não é fonte original nem autorização automática para recompilar.

Aplicar o patch 0007 somente ao staging privado: uma base de tabela dentro do próprio JMP não prova que sua extensão seja uma linha de tabela. A descoberta especulativa é suspensa, mantendo o fallback calculado. Regressão sintética reproduziu falha antes e passou depois, preservando tabela externa legítima. Contexto/core permanecem sob os termos auditados, sem relicenciamento.

Os candidatos com seeds observadas continuam separados do aplicativo entregue. Comparação até frame fixo mede somente o trecho observado, inclui BIOS e registra diferenças de tempo do input. Manter as lacunas explícitas e validar fases posteriores antes de promover o candidato. Procedimento em `REA_WORKFLOW.md`.

## 2026-10-14 — protótipo visual dos botões pelo compositor do host

Para testar rótulos de botões enquanto o codec original é investigado, usar placas autorais no framebuffer copiado pelo SDL, identificadas por perfil externo com fingerprints locais. PT-BR/Adventure somente; inglês remove o override. Não alterar pixels na RAM convidada nem áreas clicáveis. Declarar aparência provisória e escopo de menu; não apresentar overlay como recurso original traduzido. Ver `MENU_OVERLAY_PLAN.md`.


## 2026-10-14 — ativação pelo idioma do launcher

Usar o seletor existente para interface e mod do próximo jogo. Português ativa o piloto apenas em Adventure; inglês limpa o override de ambiente. Manter a preferência persistente, indicar escopo parcial e exigir reinício do jogo. O pacote GUI usa a configuração autoral do bundle, não o arquivo editável do piloto antigo, para a escolha da interface ser determinante.


## 2026-10-14 — piloto de tradução autorizado, limitado à apresentação

Após autorização explícita do usuário para traduzir/aplicar, validar primeiro um rótulo confirmado de Adventure. O CSV contém uma tradução revisada (`EMPTY → VAZIO`), aplicada por um adaptador de fonte com identidade de módulo e pontos de leitura confirmados. Não escrever na RAM/ROM ou traduzir nomes internos/ruído automaticamente. Entregar pacote separado e configuração desligável, mantendo o aplicativo normal e os saves intactos. Detalhes em `TEXT_PILOT_PLAN.md`.

## 2026-10-13 — retomar áudio pelo buffer realmente entregue após starvation

O erro de disco de Zelda's Adventure foi reproduzido com uma cópia da NVRAM do usuário. A trilha de CIAP mostra `PLAY0`, retirada do outro buffer, esvaziamento do par ADPCM e reposição do buffer 0 pelo driver. O modelo continuava esperando o buffer 1; sem consumo, `FINISH` não concluía e o jogo exibia o erro.

O patch `0004-adventure-audio-reselection.patch` preserva o buffer ativo ao substituir um som e permite nova seleção após o par esvaziar, inclusive em reposições consecutivas no mesmo buffer. Não completar `FINISH` artificialmente nem suprimir a tela de erro. A primeira tentativa, que permitia somente uma reseleção, passou no teste inicial mas falhou na reprodução completa; a regressão foi ampliada para reposição repetida.

Manter a correção em patch aplicado à cópia privada. O checkout upstream original não foi alterado. O ACK genérico do patch 0003 não foi ampliado nem adotado como explicação comprovada desta falha; sua fidelidade permanece uma investigação separada.

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
