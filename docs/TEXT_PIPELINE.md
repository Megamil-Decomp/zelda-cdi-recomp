# Pipeline de descoberta e tradução de texto

## Escopo e aceitação

Pedido de 2026-10-14: automatizar descoberta/exportação, traduzir externamente e preparar uma aplicação posterior. Nesta etapa: extração somente leitura e validação de um catálogo intermediário. Não implementar tradução de imagens/voz nem injetar bytes sem confirmar a representação e a apresentação do texto.

Aceitação: entrada comercial intacta; candidatos com localização/ID e revisão da mídia; exportação CSV/JSON; tradução externa UTF-8; validação de identidade, original, revisão e placeholders; testes sintéticos para limites de setor, dados binários e CSV alterado. O catálogo não deve ser confundido com textos confirmados nem com um mod pronto.

## 1. Extrair automaticamente

```sh
python3 scripts/text_catalog.py extract --game adventure \
  --output data/private/localization/adventure-catalog-v2.json
```

Use `--game faces` ou `--game wand` com um nome de saída correspondente para os outros títulos. O padrão de saída é de Adventure: sempre indicar `--output` ao mudar de jogo. `--cue` aceita outro CUE do perfil suportado. Saídas existentes são recusadas para evitar sobrescrever trabalho traduzido.

Saídas:

- `*.json`: catálogo e identidade SHA-256 privada da mídia; ocorrências/endereço físico completo.
- `*.csv`: todos os candidatos após filtro heurístico básico.
- `*.review.csv`: fila prioritária de candidatos de confiança heurística alta e terminados por NUL. Ainda inclui falsos positivos.

A busca usa sequências ASCII imprimíveis, sem exigir aspas; depois de compilado, o programa normalmente não conserva delimitadores do código-fonte. A heurística não entende o jogo. Comprimento padrão de 4 a 1024 bytes; `--min-length`, `--max-length` e `--include-noise` ajustam a coleta.

O extrator lê payloads Form 1, pula Form 2/inválidos e não junta texto através dessas lacunas nem após EOF. Strings entre dois setores contíguos preservam os spans físicos separados: os cabeçalhos raw não fazem parte da string. Não decodifica compressão, codificações próprias, UTF-16, fontes indexadas, imagens ou voz. Adjacência física ainda não comprova limite de arquivo ou existência de texto.

## 2. Traduzir fora do projeto

Começar por uma cópia do `*.review.csv`, editável em um editor CSV/LibreOffice/Excel. Manter codificação UTF-8 e estrutura CSV. Não alterar `id` nem `original`; preencher `translation` e marcar `reviewed=true` apenas quando o candidato foi reconhecido como texto real e a tradução revisada. Linhas vazias são ignoradas; um CSV parcial também é aceito.

Os IDs começam com `t_` para evitar conversão numérica em planilhas. Originais que começam com operadores de fórmulas recebem apóstrofo de proteção na exportação; preservar esse campo. Candidatos repetidos possuem IDs por ocorrência, porque textos iguais podem ter contextos distintos. Ferramentas externas podem propagar traduções repetidas, mas a revisão deve considerar o contexto.

## 3. Validar o arquivo traduzido

```sh
python3 scripts/text_catalog.py validate \
  data/private/localization/adventure-catalog-v1.json \
  data/private/localization/adventure-catalog-v1.review.csv \
  --output data/private/localization/adventure-pt-BR-v1.json
```

O exemplo usa o catálogo v1 já extraído. Ao criar outro catálogo, passar o par JSON/CSV correspondente.

Rejeita IDs desconhecidos/duplicados, originais alterados, traduções sem revisão, NUL e diferenças em placeholders como `%s`, `%02d` e `{name}`. Texto maior que a sequência original gera aviso, não truncamento: um futuro compositor externo pode acomodá-lo, mas uma substituição binária não pode presumir essa capacidade. Saída com `runtime_supported=false` é pacote intermediário, não mod instalado.

Exit 0: etapa concluída; 2: configuração/entrada/I/O inválida; 3: tradução reprovada. Os relatórios e textos extraídos permanecem em `data/private/`, ignorados pelo Git. A ferramenta não envia conteúdo a nenhum serviço e não traduz automaticamente.

## 4. Aplicar no jogo — piloto restrito e integração geral futura

Para cada grupo de textos reais, identificar a rotina de desenho, codificação, fonte, buffers e revisão. Integrar um adaptador no runtime para consultar IDs e desenhar traduções externas com suporte a acentos e quebras de linha. A análise de apresentação precisa ser feita por família de recursos, não por todas as linhas manualmente.

Uma substituição cega na imagem pode atingir código de máquina ou metadados, ultrapassar buffers e invalidar CRCs de módulos e identidades de recompilação. `byte_length` e `nul_terminated` não definem capacidade gravável. Por isso não há comando de injeção nesta ferramenta. ROM, BIOS e saves continuam intactos, e o objetivo permanece um mod opcional desligável.

## Execução real desta etapa

Adventure Europe: 23.749 setores Form 1, 196.151 Form 2, nenhum setor estruturalmente inválido na leitura suportada. Exportados **50.291 candidatos**, sendo **633 na fila prioritária**. Contagens de candidatos não são contagens de frases do jogo. `EMPTY` e `Zelda Saves` foram encontrados; falso positivo continua comum.

Arquivos já prontos: `data/private/localization/adventure-catalog-v1.json`, `.csv` e `.review.csv`. Validação do CSV não traduzido passou com zero traduções, sem modificar mídia. Suite: 29 testes passaram (9 novos do catálogo e 20 existentes). Posteriormente, um adaptador restrito aplicou `EMPTY` → `VAZIO` em Adventure, confirmado visualmente; veja [TEXT_PILOT_PLAN.md](TEXT_PILOT_PLAN.md). O JSON geral ainda não é consumido pelo runtime. A suite atual tem 33 testes aprovados, além de 3 testes nativos selecionados.
