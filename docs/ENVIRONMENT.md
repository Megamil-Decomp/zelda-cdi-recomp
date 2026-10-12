# Ambiente verificado

Verificação local em 2026-10-12. Relatório completo privado: `data/private/environment.json`.

| Item | Resultado observado |
| --- | --- |
| Sistema | macOS 27.0.1, build 26A434 |
| CPU | arm64, 12 CPUs lógicas |
| Memória | 64 GiB |
| Compilador | Apple Clang 21.0.0, target arm64-apple-darwin27.0.0 |
| Xcode | Xcode.app, SDK macOS disponível |
| CMake | 4.4.4 |
| Python | 3.9.6; ferramentas próprias usam somente biblioteca padrão |
| Git | 2.54.0 (Apple Git-157) |
| Make | GNU Make 3.81 |
| SDL2 | interface 2.32.70 via sdl2-compat, sobre SDL3; pacote CMake disponível no Homebrew |
| Ninja / pkg-config | não encontrados no PATH; não necessários com Unix Makefiles e SDL2 CONFIG |
| Diretório principal | ainda não é um repositório Git; nenhum commit/push realizado |

Reproduzir:

```sh
python3 scripts/diagnose_environment.py --json data/private/environment.json
```

Não foi necessário instalar pacotes. A configuração do runner usa `-DCMAKE_PREFIX_PATH=/opt/homebrew` neste host. Usar uma instalação de SDL2 compatível em cada plataforma; presença da biblioteca não comprova áudio/vídeo fiel.

O frontend upstream compilou e passou 6 testes; 11 testes de componentes do runtime também passaram. O executável completo não foi ligado porque faltam funções da BIOS recompilada. Veja comandos, commit e limitações em [UPSTREAM_AUDIT.md](UPSTREAM_AUDIT.md).
