# Exportação privada para outro Mac

## Plano e aceitação

Preparar uma cópia portátil do aplicativo aceito com BIOS e três pares CUE/BIN locais dentro de `Contents/Resources/LocalMedia`. Essa cópia continua exclusivamente em `dist/`, ignorada pelo Git. Preservar originais, saves, pacote principal e licenças. Remover a raiz absoluta da máquina de origem do manifesto. A detecção de mídia interna deve funcionar após mover o aplicativo, inclusive quando o macOS muda o caminho de execução.

Validar hashes das mídias contra o manifesto do aplicativo antes e depois da cópia, destinos relativos contidos, runtimes completos e dependências empacotadas. Conferir assinatura, integridade do ZIP e interface com preferências novas. Testes das ferramentas usam apenas fixtures sintéticas. O pacote é para Apple Silicon com macOS 13 ou posterior; não é um port Intel nem certificação da campanha completa.

## Gerar novamente

`python3 scripts/export_private_macos.py` compila o launcher atual na cópia de exportação e usa os três runtimes já aceitos em `dist/Zelda CD-i.app`. Não recompila BIOS/jogos nem altera a mídia original. Após atualizar os runtimes aceitos no aplicativo principal, executar o mesmo comando exporta a nova versão. O comando cria uma nova pasta datada em `dist/exports/` e um ZIP com um único `.app` completo; não sobrescreve uma exportação anterior. `--source-app` escolhe outro aplicativo aceito e `--output` escolhe uma pasta nova explicitamente.

No destino, descompactar e abrir `Zelda CD-i.app`. A interface identifica as mídias internas. Pode mover esse aplicativo inteiro para outra pasta; não mover apenas o executável dentro dele. Saves novos ficam no suporte de aplicação do usuário desse Mac. O macOS pode solicitar autorização na primeira abertura porque a assinatura é local, sem notarização Apple.
