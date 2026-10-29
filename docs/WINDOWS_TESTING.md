# Testar o pacote Windows x64

Primeira versão experimental, cross-compilada no Mac. Windows 10 1903+ ou Windows 11, x64. Ainda exige teste real no Windows: compilar e conferir os arquivos não certifica áudio, controles, desempenho ou campanha nesse sistema.

## No computador de teste

1. Extraia todo o ZIP `Zelda-CDi-Windows-Completo.zip`.
2. Abra `Zelda CD-i Windows/ZeldaCDi.exe`.
3. Escolha um dos três jogos e clique em **Iniciar jogo**. A interface confere os hashes e prepara a BIOS no cache do usuário. Se aparecer o player do CD-i, use **Play CD-i**.

Não precisa de Python, REA, compilador ou instalação de SDL no destino. Mantenha toda a pasta extraída junta. Os três runtimes usam a mesma investigação e as correções aceitas no Mac, compiladas para x64; não são executáveis ARM64 renomeados.

Saves e logs ficam em `%LOCALAPPDATA%\ZeldaCDiNative`, separados por título; os botões **Saves e logs** e **Abrir log** ajudam a encontrá-los. A exportação não inclui os saves pessoais do Mac. Fechar a janela do jogo ou usar **Parar** solicita o encerramento normal; a interface não mata o processo à força. O mod PT-BR é opcional e parcial em Adventure.

## Gerar novamente neste Mac

```sh
python3 scripts/export_private_windows.py
```

O gerador verifica as fontes dos candidatos aceitos pelo catálogo privado e pelo manifesto do aplicativo principal, compila runtimes x64 e launcher Win32, copia a mídia local e a SDL2 e cria uma nova pasta datada em `dist/exports-windows/`. Não altera o aplicativo macOS ou o checkout upstream. O build reaproveita objetos já compilados quando os inputs são idênticos. Atualizar o catálogo/app aceitos é uma etapa anterior de validação, comum aos dois exportadores.

Pré-requisitos do gerador: MinGW x64 (`brew install mingw-w64`), CMake e as builds/fontes aceitas locais. O primeiro uso obtém somente o SDK SDL2 oficial, com hash fixado; nenhum jogo/BIOS é baixado. `--output` define uma pasta privada nova; `--skip-build` reutiliza binários Windows apenas quando sua identidade/proveniência permanece compatível. O destino Windows recebe só o ZIP, sem esses pré-requisitos.

Verificações automáticas: fontes/runtime aceitos por SHA-256; mídias antes/depois da cópia; PE x64 dos quatro executáveis e SDL2; dependências não sistêmicas presentes; CUE/BIN preservados; licenças incluídas; teste de integridade do ZIP. Código gerado, SDK, mídia, hashes privados e pacotes continuam ignorados no Git.
