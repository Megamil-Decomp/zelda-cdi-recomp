# Adaptações locais do runtime

Aplicar somente à cópia privada em `build/native/source/`. O checkout original em `upstream-cdirecomp/` permanece intacto.

`0001-graceful-launcher-shutdown.patch` registra SIGTERM/SIGINT por uma flag `sig_atomic_t`. O loop normal encerra o player e passa pela gravação existente de NVRAM. O handler não executa I/O nem muda estado convidado. Isso permite ao botão de encerramento do launcher pedir uma saída normal; código convidado travado dentro de uma chamada pode continuar sem responder, o que deve ser informado.

`0002-performance-pacing-audio-vsync.patch` desativa os anéis de trace e hashing de depuração por padrão durante a execução normal, ajusta o pacing para 20 ms com classe de QoS interativa no Apple Silicon, aumenta o buffer de áudio para 2048 amostras prevenindo underruns, desativa VSync bloqueante e adiciona medidor de FPS em tempo real no título da janela.

`0003-stability-and-adventure-cd-fix.patch` elimina causas de encerramento inesperado do jogo (evita crash ao falhar captura de mouse no SDL ou em alternância de foco; protege a tecla ESC exigindo atalho Cmd+Q/Cmd+Esc) e soluciona a falha de leitura de disco ("disco retirado ou sujo") na transição de telas do *Zelda's Adventure* ao fornecer resposta de confirmação (`A5 <cmd> 00`) para comandos IKAT de Canal C não modelados (ex.: `$F1`, `$F2`, `$F9`, `$8x`).

Base: `mstan/cdirecomp` commit `f3c8d579efb11d5a33c6bc7c935dfbced773e62e`. O contexto do patch pertence ao upstream e mantém seus termos de licença; a adaptação não relicencia o runtime. Não contém código gerado de BIOS/discos.
