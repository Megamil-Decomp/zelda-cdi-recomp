# Aplicativo macOS experimental

O pacote `Zelda CD-i.app` é um launcher nativo para os runtimes privados gerados com a mídia local. A lista inclui Faces of Evil, Wand of Gamelon e Zelda's Adventure conforme o manifesto da compilação. O estado **Em teste** significa que a compatibilidade ainda está em validação; abrir o runtime não comprova que um jogo esteja jogável nem que toda a execução seja recompilação estática.

## Uso

1. Abra `Zelda CD-i.app` e escolha o jogo na lista.
2. Em **BIOS CD-i**, escolha a BIOS compatível com esta compilação.
3. Em **Disco do jogo**, escolha o arquivo `.cue`. Também é possível escolher o `.bin` quando existe um CUE com o mesmo nome na mesma pasta.
4. Clique em **Iniciar jogo**. O aplicativo verifica o SHA-256 da BIOS e do BIN antes de iniciar; essa leitura ocorre em segundo plano e exibe progresso.
5. Use a janela do jogo. **Parar** solicita o encerramento do runtime. **Abrir log** mostra a saída da sessão para diagnóstico.

O aplicativo lembra os caminhos por jogo. CUE e BIN precisam continuar juntos; mover ou renomear um deles exige selecionar o disco novamente. A seleção não copia os discos para o aplicativo. Nesta versão, o descritor precisa conter uma faixa `CDI/2352` ou `MODE2/2352`, um único BIN na mesma pasta e `INDEX 01 00:00:00`, sem pregap.

A identidade dos arquivos está vinculada ao código recompilado incluído no pacote. Outra revisão de BIOS ou disco é rejeitada com uma explicação e exige uma compilação correspondente.

## Arquivos locais

- Preferências de seleção: domínio de preferências do identificador do aplicativo.
- Dados por jogo e NVRAM: `~/Library/Application Support/ZeldaCDiNative/<id-do-jogo>/`. O runtime usa `player.cfg` e `nvram.bin` nessa pasta.
- Firmware normalizado, quando necessário: `~/Library/Application Support/ZeldaCDiNative/firmware/`.
- Logs de execução: `~/Library/Logs/ZeldaCDiNative/`.

A BIOS fornecida com palavras de 16 bits invertidas é validada pelo hash original, convertida em uma cópia privada e validada novamente pelo hash esperado pelo runtime. O arquivo original é preservado. Uma BIOS que já está normalizada também é aceita quando seu hash corresponde ao manifesto.

O menu **Arquivo → Abrir pasta de dados** abre os dados persistentes. Fechar o launcher durante uma sessão pede confirmação para solicitar o encerramento do jogo. O runtime é um processo separado; o launcher informa seu código de saída no final e conserva o log.

## Estrutura do pacote

O launcher Swift/AppKit está em `app/macos/Launcher.swift`. O pacote requer:

```text
Zelda CD-i.app/
  Contents/
    Info.plist
    MacOS/
      ZeldaCDiLauncher
      CdiRuntime-faces
      CdiRuntime-gamelon
      CdiRuntime-adventure
    Resources/
      runtime-manifest.json
```

Os nomes reais dos executáveis vêm de `games[].runtime` no manifesto. Os caminhos de runtime e identificadores são restritos a nomes simples; não podem apontar para arquivos externos ao pacote. Bibliotecas nativas adicionais são empacotadas pelo script de build.

O manifesto privado usa `schema_version: 1`, identidade da BIOS (`size`, `sha256`, `runtime_sha256` opcional e `byte_order: "swap16"` opcional), e uma lista `games` com `id`, `title`, `runtime`, `disc_sha256`, `status` e `status_text`. Opcionalmente, `local_media_root`, `bios.local_relative` e `games[].local_cue_relative` permitem preencher a mídia local na primeira abertura. Caminhos lembrados pelo usuário têm prioridade. Os hashes correspondem ao BIN, não ao texto do CUE.

BIOS, discos, firmware convertido, código comercial gerado e os runtimes privados não devem entrar no Git. Este documento descreve a interface; os resultados de execução efetivamente observados são registrados em `PROGRESS.md`.
