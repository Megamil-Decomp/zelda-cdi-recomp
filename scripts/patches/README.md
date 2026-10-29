# Adaptações locais do runtime

### 0010 — opções do player, pausa e mouse livre

Integra os três headers autorais `cdi_player_ui*.h` ao SDL. F1/Start abre opções; o loop principal processa janela/sinais sem avançar CPU/dispositivos. Volume altera somente a cópia PCM de saída; preferências ficam em `frontend.cfg`. Mouse habilitado e captura são estados separados, com deltas de coordenadas lógicas quando livre; F2 alterna confinamento. Analógico esquerdo usa deadzone para direções. Abrir o menu descarta movimentos/cliques pendentes, e retomar espera controles neutros para evitar ações involuntárias.

Aplicar apenas em staging privado após as adaptações anteriores; não editar o checkout upstream. O contexto permanece sob os termos auditados. Fonte bitmap do novo menu é autoral; nenhum recurso dos discos é incorporado. Plano e testes em `docs/PLAYER_MENU_PLAN.md`. Mac 0.1.7 é o primeiro pacote; o ZIP Windows anterior não recebe mudanças retroativamente.

`0005-adventure-menu-text-pilot.patch` integra o adaptador autoral `app/native/cdi_text_mod.h`, copiado pela pipeline. Traduz somente um rótulo confirmado (`EMPTY`) nas rotinas de desenho e medição da fonte da revisão Adventure compilada, sem alterar bytes físicos ou lógica de saves. Exige configuração externa explícita; ausente, inválida ou desligada mantém o original. Pacote piloto e limites documentados em `docs/TEXT_PILOT_PLAN.md`.

`0004-adventure-audio-reselection.patch` corrige a retomada do ADPCM quando o par de buffers esvazia e o driver repõe o mesmo buffer. Preserva o áudio ativo ao substituir um som; a próxima seleção ocorre após seu término e segue o buffer realmente entregue. Inclui regressão sintética que falha no runtime anterior. Não altera ROM, save, lógica do jogo ou o erro de leitura para forçar sucesso.

Aplicar somente à cópia privada em `build/native/source/`. O checkout original em `upstream-cdirecomp/` permanece intacto.

`0001-graceful-launcher-shutdown.patch` registra SIGTERM/SIGINT por uma flag `sig_atomic_t`. O loop normal encerra o player e passa pela gravação existente de NVRAM. O handler não executa I/O nem muda estado convidado. Isso permite ao botão de encerramento do launcher pedir uma saída normal; código convidado travado dentro de uma chamada pode continuar sem responder, o que deve ser informado.

`0002-performance-pacing-audio-vsync.patch` desativa os anéis de trace e hashing de depuração por padrão durante a execução normal, ajusta o pacing para 20 ms com classe de QoS interativa no Apple Silicon, aumenta o buffer de áudio para 2048 amostras prevenindo underruns, desativa VSync bloqueante e adiciona medidor de FPS em tempo real no título da janela.

`0003-stability-and-adventure-cd-fix.patch` trata encerramentos por falha de captura de mouse/troca de foco e exige Cmd+Q/Cmd+Esc para saída por teclado. Também acrescenta respostas genéricas (`A5 <cmd> 00`) a comandos IKAT de Canal C. A alegação anterior de que essas respostas resolviam o erro de disco de Adventure não se sustentou na reprodução de 13/10; a fidelidade desse fallback ainda precisa de investigação. A causa de áudio observada nessa reprodução é tratada no patch 0004.

Base: `mstan/cdirecomp` commit `f3c8d579efb11d5a33c6bc7c935dfbced773e62e`. O contexto do patch pertence ao upstream e mantém seus termos de licença; a adaptação não relicencia o runtime. Não contém código gerado de BIOS/discos.

### 0006 — compositor opcional do menu de Adventure

Integra o header autoral `app/native/cdi_menu_mod.h` no frontend SDL. O perfil externo `CDI_MENU_MOD_PATH` fornece fingerprints e rótulos autorais. Nenhum pixel comercial ou hash local é fixado no código; composição ocorre na cópia do framebuffer, sem tocar memória convidada ou hitboxes. Protótipo visual de cinco botões, não decodificador/substituição do recurso gráfico original. Plano, limites e aceitação em `docs/MENU_OVERLAY_PLAN.md`.

### 0007 — base de tabela dentro do próprio JMP

Impede a descoberta especulativa de tabela PC-indexada quando a base calculada aponta para dentro da instrução de despacho. Uma palavra de extensão zero era tomada como primeira entrada de tabela, inventando fluxo por dados. Preserva o fallback para o destino realmente calculado; entradas descobertas independentemente continuam disponíveis. A regressão sintética reproduz a falha anterior e confere que tabelas externas legítimas continuam suportadas.

Aplica-se somente ao core na cópia privada. Base core `ddfa4e1b090b643a9ee596050e7eb345b8b276a2`, contido no upstream fixado acima; contexto e código adaptado permanecem sujeitos aos termos não comerciais auditados em `docs/UPSTREAM_AUDIT.md`. Não contém bytes, offsets ou hashes de mídia comercial. Investigação REA e limites em `docs/REA_PILOT_PLAN.md`.

### 0008 — janela de decodificação sem leituras especulativas de MMIO

O intérprete copiava 64 bytes pelo barramento antes de executar a instrução. Perto de limites de RAM/ROM, essa especulação podia reconhecer/limpar status de interrupção ou ler um registrador de vídeo somente de escrita e abortar o host. A janela agora usa somente o span RAM/ROM disponível e rejeita instruções que exigem extensões ausentes; operandos reais continuam usando o barramento e a exceção existente.

Fetch fora desses spans continua falhando explicitamente (`BADADDR`); este patch não implementa o frame arquitetural de erro de instruction-fetch em MMIO. Não introduz valores de retorno inventados em registradores. Regressão sintética compara antes/depois, preserva CSR adjacente e verifica o erro de operando real. Aplicar somente ao staging; contexto permanece sob os termos upstream auditados.

### 0009 — prioridade no reconhecimento de interrupção

Após salvar o SR anterior no frame, o reconhecimento de IRQ passa a elevar a máscara IPL ao nível aceito e desativar o trace da CPU, conforme Philips SCC68070, especificação de abril de 1993, seção 5.11, página 23 ([arquivo de documentação](https://www.icdia.co.uk/docs/scc68070.zip)). Antes, a rotina verificava a máscara para aceitar a IRQ mas não a atualizava ao entrar, permitindo nova entrada no mesmo nível.

Fixture autoral confere frame com SR/PC/vetor originais, pilhas de usuário/supervisor, reentrada bloqueada, preempção por nível superior, fonte on-chip e restauração do contexto. Não altera temporização CIAP, comandos da BIOS ou bytes do jogo. Aplicação somente no staging; contexto e termos upstream são os auditados acima.
