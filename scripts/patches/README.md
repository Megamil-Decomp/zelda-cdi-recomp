# Adaptações locais do runtime

Aplicar somente à cópia privada em `build/native/source/`. O checkout original em `upstream-cdirecomp/` permanece intacto.

`0001-graceful-launcher-shutdown.patch` registra SIGTERM/SIGINT por uma flag `sig_atomic_t`. O loop normal encerra o player e passa pela gravação existente de NVRAM. O handler não executa I/O nem muda estado convidado. Isso permite ao botão de encerramento do launcher pedir uma saída normal; código convidado travado dentro de uma chamada pode continuar sem responder, o que deve ser informado.

Base: `mstan/cdirecomp` commit `f3c8d579efb11d5a33c6bc7c935dfbced773e62e`. O contexto do patch pertence ao upstream e mantém seus termos de licença; a adaptação não relicencia o runtime. Não contém código gerado de BIOS/discos.
