# Mídia local e verificação

Os arquivos já fornecidos bastam para a auditoria. Nenhum download de jogo ou BIOS é necessário. Os caminhos abaixo são relativos à raiz do projeto; não renomear apenas o BIN sem atualizar o CUE.

| Uso | Caminho local |
| --- | --- |
| Faces of Evil: descritor | `roms/Link The Faces of Evil/Link - The Faces of Evil (Europe).cue` |
| Faces of Evil: disco | `roms/Link The Faces of Evil/Link - The Faces of Evil (Europe).bin` |
| Wand of Gamelon: descritor | `roms/Zelda The Wand of Gamelon/Zelda - The Wand of Gamelon (Europe).cue` |
| Wand of Gamelon: disco | `roms/Zelda The Wand of Gamelon/Zelda - The Wand of Gamelon (Europe).bin` |
| Zelda's Adventure: descritor | `roms/Zeldas Adventure/Zelda's Adventure (Europe).cue` |
| Zelda's Adventure: disco | `roms/Zeldas Adventure/Zelda's Adventure (Europe).bin` |
| BIOS principal para o caminho atual do upstream | `bios/cdi490a.rom`, tamanho esperado 524288 bytes |
| Firmware DVC disponível, necessidade ainda não demonstrada | `bios/impega.rom`, `bios/vmpega.rom`, 262144 bytes cada |

O tamanho esperado da BIOS não identifica revisão/autenticidade. Não assumir que o runtime suporta o DVC por esses arquivos estarem presentes. A necessidade de MPEG e os codecs efetivos das cinematics de cada título precisam ser investigados.

## Comandos locais

```sh
python3 scripts/verify_local_media.py --json data/private/media-report.json
python3 scripts/verify_local_media.py --scope faces
python3 scripts/verify_local_media.py --write-manifest data/private/media-lock.json
python3 scripts/verify_local_media.py --manifest data/private/media-lock.json
```

O manifest é um registro pessoal dos arquivos atuais para detectar alterações futuras. Não é uma base externa confiável e não certifica os dumps. `data/private/media-lock.json` já foi criado nesta auditoria; use `--manifest` para comparar com ele. A criação recusa sobrescrever um lock existente.

O verificador confere presença, tamanho, SHA-256, relação CUE/BIN, campos essenciais do Disc Label e amostras de cabeçalhos Mode-2/subcabeçalhos. Exit 0 indica verificações suportadas aprovadas, com possíveis avisos; exit 2 indica erro de configuração/manifest/I/O; exit 3 indica mídia ausente, estrutura amostrada inconsistente ou divergência de hash. A amostragem não verifica todo o disco, EDC/ECC, codecs ou todos os recursos. Os hashes completos ficam nos relatórios privados; não há hashes canônicos inventados nesta documentação.

Nesta execução foram inventariados 9 arquivos e examinados 35 setores distribuídos por volume em cada disco. Verificação e comparação posterior com o lock retornaram exit 0. Faces e Wand têm setores além do volume declarado e preenchimento uniforme na cauda; foram relatados como avisos, sem certificar a faixa extra nem concluir corrupção. Adventure não apresentou setores fora do volume declarado.

## Inventário observado

O `CdiRecomp` do commit registrado em `UPSTREAM_AUDIT.md`, compilado neste Mac e executado sem `--emit`, retornou exit 0 nos três discos:

| Disco | Volume no LBA 16 | Módulos encontrados | Paridade / CRC dos módulos encontrados |
| --- | --- | --- | --- |
| Faces of Evil | CD-I | 5 | todos válidos |
| Wand of Gamelon | CD-I | 5 | todos válidos |
| Zelda's Adventure | CD-I | 4 | todos válidos |

Isso demonstra que o parser encontrou módulos nos extents examinados. Não demonstra execução, extração de todos os recursos ou completude da descoberta de código. Logs detalhados: `data/private/inventory-faces.log`, `inventory-gamelon.log` e `inventory-adventure.log`.

## Armazenamento

- Manter mídia em `roms/` e `bios/`; relatórios, locks, recursos extraídos e rastros em `data/private/`; código gerado e binários em `build/` ou `data/private/`.
- Esses caminhos estão ignorados pelo Git. Não usar `git add -f` para contornar as exclusões.
- Um `.gitignore` não remove arquivos já versionados. Ao iniciar o repositório, revisar a lista de arquivos preparados antes de qualquer commit.
- Para um futuro teste mínimo de Faces, somente o par BIN/CUE de Faces e a BIOS principal são exigidos pela preparação atual. Os outros títulos ficam para marcos posteriores.
