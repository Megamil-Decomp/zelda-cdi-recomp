# Portabilidade: avaliação em 2026-10-29

Avaliação do código local e da documentação dos SDKs. Após esta avaliação, os três runtimes e um launcher Win32 foram cross-compilados para Windows x64, com exportador privado reutilizável; veja [teste Windows](WINDOWS_TESTING.md). A execução real no Windows continua pendente. Vita/3DS não foram compilados. Níveis abaixo são estimativas de engenharia, não prazos garantidos.

| Destino | Complexidade estimada | Trabalho principal |
| --- | --- | --- |
| Windows x64 | Média; menor entre os novos alvos examinados | Compilar o C gerado, validar runtime e DLLs, criar launcher e empacotamento Windows |
| PS Vita | Alta | Adaptar serviços do host, controles/tela, armazenamento e pacote homebrew; medir CPU/RAM e reduzir depuração |
| Nintendo 3DS | Muito alta, viabilidade de desempenho por provar | Mesmos serviços, mais atenção a renderização, concorrência e orçamento de CPU/memória |

## Windows primeiro

A geração atual produz C, compilado para ARM64 no Mac. O mesmo C pode ser compilado para outra arquitetura, desde que runtime e compilador suportem as operações usadas. Isso reaproveita a investigação e as correções dos jogos; não transforma um `.app` já pronto em `.exe` e não garante ausência de diferenças de plataforma.

No staging auditado, `runner/CMakeLists.txt` já trata MSVC/MinGW, SDL2, Winsock e cópia de DLL. `runtime.c` tem temporização por QueryPerformanceCounter/waitable timer; o servidor de debug, a NVRAM e o relógio têm caminhos `_WIN32`. Essa base reduz o trabalho inicial. A GUI é Swift/AppKit e os scripts de build/assinatura são macOS: precisam de equivalentes para Windows. SDL tem [suporte Windows documentado](https://wiki.libsdl.org/SDL2/README-windows).

Sequência proposta: prova do runtime x64 de Faces com mídia local e testes sintéticos; reprodução de IRQ/fetch/primeira área; repetir Adventure/Gamelon; só depois launcher com seletor, validação SHA-256, saves e mod opcional; finalmente ZIP portátil com dependências, testado numa instalação Windows sem ambiente de desenvolvimento. Não publicar mídia nem C comercial gerado no CI/Git. Manter comparações privadas e medir fallback também nesse destino.

## Portáteis

Existe [SDL2 para Vita com VitaSDK/CMake](https://wiki.libsdl.org/SDL2/README-vita), mas presença da biblioteca não prova que nosso runtime caiba ou tenha desempenho suficiente. Precisamos rever os buffers de depuração alocados, serviços POSIX, I/O de disco, temporização, UI e pacote de instalação; avaliar em hardware real.

Existe [SDL2 para 3DS com devkitARM/CMake](https://wiki.libsdl.org/SDL2/README-n3ds). A documentação atual registra renderização apenas por software e concorrência cooperativa no backend; são riscos concretos para o nosso vídeo e servidor de depuração. Um backend específico, redução de memória e mais cobertura estática podem ser necessários. Não prometer funcionamento em Old/New 3DS antes de um protótipo medido.
