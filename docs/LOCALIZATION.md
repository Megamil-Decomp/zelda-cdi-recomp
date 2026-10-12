# Localização PT-BR — proposta, sem implementação

Estado em 12/10/2026: requisito futuro. Não foram traduzidos textos nem extraídos, substituídos ou publicados recursos comerciais. A prioridade é validar a execução original de Faces of Evil.

## Princípios e fronteira

O mod será opcional, selecionado em configuração externa e ativável/desativável sem recompilar o jogo. Desativado, a camada deve sair imediatamente sem alterar textos, áudio, layout, entradas, RNG, estado de jogo ou tempo convidado. Ativado, pode mudar a apresentação do texto/legenda, mantendo lógica e áudio originais. Os dados originais continuam sendo lidos do disco privado; não sobrescrever a imagem, módulos OS-9 ou saves para instalar uma tradução.

O runtime produz eventos semânticos de apresentação somente depois de identificar o caminho real: por exemplo, “texto de menu identificado”, “início de sequência” ou “fim de fala”. Um adaptador por jogo/revisão converte esses eventos em IDs estáveis. A camada de mod consulta JSON UTF-8 externo e desenha o resultado no compositor do host. Não inserir traduções ou lógica linguística no C gerado pelo recompilador.

Uma chamada UCM pode ser ponto de observação, mas não presumir que todos os textos passam por ela. Fontes em bitmap, caracteres desenhados por blits próprios ou palavras já presentes em imagens exigem outra investigação. Substituições devem ter escopo exato de versão/contexto; busca global de strings em RAM é inadequada como arquitetura permanente.

## O que já se sabe e o que falta descobrir

Os inventários privados reconheceram módulos OS-9 dos três jogos; não classificaram seus recursos linguísticos. Ainda estão desconhecidos armazenamento/codificação dos textos, tabelas de glifos, mapeamento de falas e formatos efetivos de cinematics. Ausência de strings legíveis no executável não prova ausência de texto.

O padrão CD-i oferece formatos de imagem como CLUT/DYUV e animações RL3/RL7, além de áudio ADPCM. Esses são candidatos para investigação, não identificação dos codecs usados pelos jogos locais. Cinematics não devem ser presumidas arquivos MPEG ou vídeos independentes. [Boletim técnico OptImage, pp. 5–7](https://icdia.co.uk/authoring/cdi_standards.pdf). O MCD212 de referência implementa paleta, transparência, ordem de planos e mistura; uma sobreposição de tradução terá de respeitar a composição observada. [MAME, `mcd212.cpp`](https://github.com/mamedev/mame/blob/master/src/mame/philips/mcd212.cpp).

| Recurso | Investigação local futura | Resultado a registrar, sem publicar o recurso |
| --- | --- | --- |
| Strings de menus, inventário e interface | Correlacionar leitura do disco, referências de módulo e chamadas/desenhos durante um cenário reproduzível | Codificação, terminadores, limites, ID/contexto e ponto de apresentação |
| Fontes | Identificar origem da tabela, índice de glifo, métricas, largura e transparência | Mapa de caracteres e contrato do renderizador, sem copiar a fonte comercial |
| Palavras em imagens | Classificar imagem/paleta/compressão e instante de exibição | Dimensões, contexto, região e mecanismo de substituição opcional |
| Falas/cinematics | Correlacionar setores, canais, áudio, frames e eventos de início/fim/skip | Sequência, base temporal, duração e formato comprovado |
| Texto desenhado por código próprio | Observar blits e tabelas com rastreabilidade por versão | Adaptador específico documentado; não prometer extração automática |

Faces of Evil terá o primeiro inventário de recursos; Wand deve repetir a análise antes de reutilizar adaptadores. Adventure terá mapa independente, inclusive para `cdi_bpsys` e `cdi_vsync_trap`: seus nomes não provam que gerenciam texto ou sincronização de legendas.

## Contrato externo proposto

Exemplo de esquema, com texto fictício autoral e identificadores ilustrativos; não é uma tradução, arquivo instalado ou API implementada:

```json
{
  "schema_version": 1,
  "game_id": "faces-of-evil",
  "locale": "pt-BR",
  "compatible_disc_sha256": ["<hash-da-revisao-validada>"],
  "font": "<fonte-autoral-ou-com-licenca-verificada>",
  "strings": {
    "ui.example": {"text": "Texto de exemplo autoral", "layout": "menu"}
  },
  "subtitles": {
    "sequence.example": [
      {"start_tick": 0, "end_tick": 120, "text": "Legenda de exemplo autoral"}
    ]
  },
  "timing": {"tick_rate_num": 60, "tick_rate_den": 1}
}
```

A taxa acima é ilustrativa; o adaptador deve fornecer a base temporal real da sequência. O manifesto da tradução identifica versão do esquema, autor/licença e revisões compatíveis. IDs devem sobreviver a mudanças de endereço em RAM. Associações a hash de módulo e offset ficam no adaptador de compatibilidade, não exigem incluir os bytes originais no pacote.

Validar tamanho máximo, tipos, intervalos, IDs duplicados, UTF-8 e compatibilidade antes de carregar. Chave ausente preserva a apresentação original; pacote incompatível não aplica substituições. Caminhos de fonte/imagem ficam limitados ao diretório do mod. Conteúdo de tradução é dado, sem scripts ou avaliação de expressões. Erros devem ser diagnósticos claros e não interromper a execução original.

## Acentos, fonte e layout

Usar UTF-8 e normalização NFC; testar `á à â ã é ê í ó ô õ ú ü ç`, maiúsculas e pontuação. Selecionar fonte autoral ou redistribuível, verificando licença e cobertura antes de incluí-la. Uma fonte do disco não se torna redistribuível por ter sido extraída.

Medir largura em pixels, altura e área segura; não usar apenas número de caracteres. Definir limites por contexto, quebras explícitas/opcionais e comportamento para palavras longas, duas linhas e texto maior. Nunca alterar buffers convidados ou aumentar seus limites como efeito incidental da tradução. Ajustes visuais são responsabilidade do compositor/adaptador, com comparação de paleta, transparência, escala e legibilidade nas resoluções originais PAL/NTSC relevantes.

## Legendas e sincronização

Ancorar cues no relógio convidado ou na posição de áudio efetivamente reproduzida, com início de sequência identificado. Evitar tempo de parede e suposições de 30/60 FPS. Pausa, seek, repetição, skip, transição e carregamento devem limpar ou reposicionar as cues. Latência do dispositivo de áudio do host deve ser tratada na apresentação sem mudar o timing original.

O pacote pode conter texto autoral e tempos; áudio e frames continuam privados/originais. Um transcript alinhado requer revisão humana e reprodução local: sem validar formato e eventos não há garantia de sincronização. Substituição de imagens com palavras só será admitida com material autoral e mecanismo específico comprovado; não incluir imagens extraídas no repositório público.

## Gates antes de implementar PT-BR

1. Faces of Evil executa o cenário original aceito, com cobertura e divergências registradas.
2. O mapa de recursos documenta ao menos um texto e uma sequência com evidência local reproduzível; sem concluir que todos seguem o mesmo formato.
3. Mod desativado mantém estado convidado e saída original no mesmo cenário; comparação pode exigir normalização apenas de fatores externos já documentados.
4. Um pacote de teste autoral valida acentos, quebra de linha, ausência de chave, revisão incompatível e erro de JSON sem modificar a execução convidada.
5. Uma sequência valida legenda com áudio original durante pausa, skip e repetição, dentro de tolerância explicitamente definida a partir do relógio medido.

Fontes, JSON autoral e documentação futura de tradutores têm licença/proveniência próprias. Extrações, C gerado, capturas, áudio e índices privados com material protegido permanecem em `data/`/`build/` ignorados. Licenças das referências técnicas e limites de reutilização constam de [ARCHITECTURE.md](ARCHITECTURE.md).
