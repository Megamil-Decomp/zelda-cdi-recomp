# Adventure — investigação dos demais textos do menu

## Aceitação e plano

Identificar separadamente strings e recursos gráficos, preservar mídia/saves e não aplicar traduções a IDs internos. Confirmar o caminho de apresentação antes de alterar o runtime. Para uma próxima substituição gráfica, exigir captura original/traduzida, idioma inglês intacto, clique/hitbox inalterados e pacote opcional.

## Evidência de 2026-10-14

- Captura do menu completo obtida por execução isolada, com cópia da NVRAM: `data/private/localization/menu-investigation/final.png`. Nenhuma mídia original foi escrita; processo de teste encerrado.
- Observação temporária da rotina já confirmada em `0x75ea` registrou `EDU` e os dois slots `EMPTY`. Não registrou os nomes dos botões. O hook também vê leituras de código, portanto o log inclui ruído; ausência neste caminho não prova ausência de outra rotina de fonte.
- Busca no executável de 133.120 bytes não encontrou PLAY, CREATE, DELETE, HOW TO PLAY ou EXIT em ASCII, UTF-16BE ou UTF-16LE. EMPTY aparece duas vezes em ASCII. Isso reforça a hipótese de botões gráficos; não confirma o codec nem a localização do bitmap.
- Dez chamadas relativas às rotinas confirmadas de desenho/medição foram catalogadas. Relatório privado: `font-call-sites.json`.
- Os arquivos `zelda.mapres` e o prefixo de `zelda.rtf` compartilham um contêiner estruturado big-endian: bloco de nomes de tabelas (`r`, `l`, `v`, `a`, `d`), tabela de offsets e blocos filhos. As tabelas `r` e `l` têm, respectivamente, registros fixos de 12 bytes e nomes variáveis terminados em NUL.
- Leitor autoral `scripts/adventure_resource_index.py` exporta nomes e seis campos uint16 brutos por registro, sem atribuir semântica não comprovada. São **47 recursos em mapres** e **193 no índice inicial de zelda.rtf**. São IDs internos, não frases traduzíveis. Mapres inclui `nvr`, `opt`, `invent`; o outro índice inclui nomes de ambientes e sequências. Não inferir o conteúdo de cada um apenas pelo nome.

Ferramenta usa somente Python padrão e não escreve no arquivo de entrada. Saída obrigatoriamente nova em `data/private/`; testes usam contêiner sintético. Foram aprovados 38 testes Python, incluindo cinco do leitor. Instrumentação temporária removida e runtime reconstruído; nenhum pacote com sondas foi distribuído.

## Próxima etapa técnica

Correlacionar o carregamento de `nvr`/`opt` com a tela exibida, determinar significado dos campos de registro e localizar o recurso gráfico real. Depois mapear codec/paleta e criar substituição autoral dos rótulos (JOGAR, CRIAR, APAGAR, COMO JOGAR, SAIR), sem mudar áreas clicáveis. Esses termos estão planejados, ainda não aplicados. Se outro caminho de fonte for encontrado, preferir adaptador de texto a imagens.

O aplicativo entregue continua traduzindo somente EMPTY → VAZIO. Não há nova versão traduzida nesta investigação.
