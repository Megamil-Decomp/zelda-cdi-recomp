# Portabilidade: avaliação em 2026-10-29

Avaliação do código local e da documentação dos SDKs. Após esta avaliação, os três runtimes e um launcher Win32 foram cross-compilados para Windows x64, com exportador privado reutilizável; veja [teste Windows](WINDOWS_TESTING.md). A execução real no Windows continua pendente. Vita/3DS não foram compilados. Níveis abaixo são estimativas de engenharia, não prazos garantidos.

| Destino | Complexidade estimada | Trabalho principal |
| --- | --- | --- |
| Windows x64 | Média; menor entre os novos alvos examinados | Compilar o C gerado, validar runtime e DLLs, criar launcher e empacotamento Windows |
| iOS (ARM64) | Média a alta | Compilar o C gerado com SDL2 iOS, controles de toque/gamepad, armazenamento no sandbox do app e assinatura/sideload privado |
| Android (ARM64) | Média a alta | Compilar com Android NDK/SDL2, empacotamento APK, interface de toque/gamepad e acesso local às mídias/saves |
| PS Vita | Alta | Adaptar serviços do host, controles/tela, armazenamento e pacote homebrew; medir CPU/RAM e reduzir depuração |
| Nintendo 3DS | Muito alta, viabilidade de desempenho por provar | Mesmos serviços, mais atenção a renderização, concorrência e orçamento de CPU/memória |

## Windows primeiro

A geração atual produz C, compilado para ARM64 no Mac. O mesmo C pode ser compilado para outra arquitetura, desde que runtime e compilador suportem as operações usadas. Isso reaproveita a investigação e as correções dos jogos; não transforma um `.app` já pronto em `.exe` e não garante ausência de diferenças de plataforma.

No staging auditado, `runner/CMakeLists.txt` já trata MSVC/MinGW, SDL2, Winsock e cópia de DLL. `runtime.c` tem temporização por QueryPerformanceCounter/waitable timer; o servidor de debug, a NVRAM e o relógio têm caminhos `_WIN32`. Essa base reduz o trabalho inicial. A GUI é Swift/AppKit e os scripts de build/assinatura são macOS: precisam de equivalentes para Windows. SDL tem [suporte Windows documentado](https://wiki.libsdl.org/SDL2/README-windows).

Sequência proposta: prova do runtime x64 de Faces com mídia local e testes sintéticos; reprodução de IRQ/fetch/primeira área; repetir Adventure/Gamelon; só depois launcher com seletor, validação SHA-256, saves e mod opcional; finalmente ZIP portátil com dependências, testado numa instalação Windows sem ambiente de desenvolvimento. Não publicar mídia nem C comercial gerado no CI/Git. Manter comparações privadas e medir fallback também nesse destino.

## Mobile (iOS e Android)

Como a recompilação produz código C estático, não depende de JIT em tempo de execução — o que evita a principal restrição técnica do iOS e simplifica o port para Android NDK (ARM64). SDL2 possui backends documentados para [iOS](https://wiki.libsdl.org/SDL2/README-ios) e [Android](https://wiki.libsdl.org/SDL2/README-android).

O escopo de cada plataforma inclui:
- Adaptação do ciclo de vida do aplicativo (suspensão/retomada de vídeo e áudio sem corromper saves/NVRAM).
- Interface de seleção, importação/leitura de BIOS e pares CUE/BIN fornecidos localmente pelo usuário (Files app / Document Picker no iOS; SAF / diretório privado do app no Android).
- Camada de controles na tela (D-pad/ponteiro CD-i, botões 1/2 e menu de opções) somada ao suporte a controles Bluetooth via SDL GameController.
- Empacotamento privado para teste local (`.ipa` assinado localmente para sideload no iOS; `.apk` no Android), mantendo mídias comerciais e C gerado fora do repositório público.

## Portáteis

Existe [SDL2 para Vita com VitaSDK/CMake](https://wiki.libsdl.org/SDL2/README-vita), mas presença da biblioteca não prova que nosso runtime caiba ou tenha desempenho suficiente. Precisamos rever os buffers de depuração alocados, serviços POSIX, I/O de disco, temporização, UI e pacote de instalação; avaliar em hardware real.

Existe [SDL2 para 3DS com devkitARM/CMake](https://wiki.libsdl.org/SDL2/README-n3ds). A documentação atual registra renderização apenas por software e concorrência cooperativa no backend; são riscos concretos para o nosso vídeo e servidor de depuração. Um backend específico, redução de memória e mais cobertura estática podem ser necessários. Não prometer funcionamento em Old/New 3DS antes de um protótipo medido.
