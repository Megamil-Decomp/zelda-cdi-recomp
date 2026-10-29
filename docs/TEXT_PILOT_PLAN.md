# Piloto PT-BR — 2026-10-14

O usuário autorizou traduzir e aplicar textos após a etapa de extração. A extração anterior cobriu apenas Zelda's Adventure; os outros dois títulos ainda não foram catalogados.

Primeiro piloto: confirmar a leitura/apresentação de `EMPTY`, visto nos slots vazios do menu, e testar `VAZIO`. Não traduzir candidatos ruidosos nem tratar nomes internos de arquivos/saves como textos visuais.

Aceitação: uma captura original e outra traduzida no mesmo menu; mídia e NVRAM originais intactas; mod opcional, separado dos bytes físicos da ROM e do binding nativo; nenhuma alteração em lógica de save; original quando desligado. Se a observação mostrar que o literal não é a fonte visual do menu, registrar isso antes de tentar outra forma de aplicação.

Não prometer tradução completa ou aplicar o CSV inteiro automaticamente. Voz, imagens e suporte geral a fontes/acentos continuam fora deste piloto.

## Resultado

Piloto implementado e verificado visualmente: os dois slots vazios mostram `VAZIO`; o nome do save permanece intacto. Captura consistente em `data/private/localization/pilot/final.png`, estado em `translation-acceptance.json`. Bytes originais dos slots continuam `EMPTY` na RAM; binding nativo continua ativo, sem invalidações ou dispatch misses. NVRAM original foi comparada à cópia anterior ao teste e permanece intacta.

O adaptador reconhece a revisão pelo binding nativo de imagem completa já verificado por SHA-256, nome/tamanho do módulo e duas leituras confirmadas de desenho/medição de texto. Ele transforma somente o valor observado pela rotina de fonte, sem escrever na memória convidada ou alterar comparações/arquivos de save. Configuração desconhecida/inválida mantém o original.

Código autoral: `app/native/cdi_text_mod.h`; integração em `scripts/patches/0005-adventure-menu-text-pilot.patch`, aplicado somente à cópia privada. Header copiado pela pipeline. O CSV revisado contém uma tradução confirmada e foi validado pelo catálogo. O adaptador piloto usa um arquivo de configuração simples, não aplica o JSON inteiro.

Testes: 33 testes Python passaram, incluindo 4 fixtures nativas do adaptador (habilitado, desligado, limites e configuração inválida); CTest de binding nativo, áudio e CIAP: 3/3 passaram. Nenhum código comercial gerado ou extração foi adicionado ao Git; nenhum commit/push realizado.

## Usar o piloto

Pacote atual 0.1.3 em `dist/ptbr-gui/Zelda CD-i.app` e `dist/ptbr-gui/Zelda-CDi-AppleSilicon.dmg`. O app normal em `dist/` não foi substituído.

O seletor de idioma existente controla a interface e o próximo processo do jogo. Português ativa o arquivo autoral externo `Contents/Resources/adventure-ptbr.txt` somente em Adventure; inglês remove `CDI_TEXT_MOD_PATH`, inclusive se herdado do ambiente, preservando o texto original. A preferência fica salva em `appLanguage`. Reiniciar o jogo para aplicar mudanças; o jogo aberto não é interrompido. Os outros títulos continuam com texto original.

A configuração antiga em Application Support não é mais consultada por este pacote: a GUI determina ativação. Este piloto aceita somente cinco letras ASCII maiúsculas para esse rótulo. Ainda não suporta tradução geral, acentos, imagens, falas ou cinematics.

Construção reproduzível após a pipeline nativa:

```sh
python3 scripts/build_macos_app.py --output dist/ptbr-gui --no-local-paths \
  --text-mod data/private/localization/pilot/adventure-ptbr.txt
```
