# Arquitetura proposta — Zelda CD-i Native Recompilation

Estado em 12/10/2026: investigação e planejamento. Os inventários locais confirmam módulos nos três discos, mas não demonstram execução nativa, cobertura integral, fidelidade ou suporte aos jogos. Nenhum port de Zelda foi implementado nesta fase.

## Evidências e limites

| Observação | Evidência | O que não demonstra |
| --- | --- | --- |
| Faces of Evil: 5 módulos reconhecidos; 2 `Prog`, 3 `Data`; principal `cdi_link`, 133.780 bytes | `data/private/inventory-faces.log`, execução local de `CdiRecomp`, sem emissão de código | Que todos os recursos ou caminhos executáveis foram descobertos |
| Wand of Gamelon: 5 módulos; 2 `Prog`, 3 `Data`; principal `cdi_zelda`, 134.464 bytes | `data/private/inventory-gamelon.log` | Que o motor é idêntico ao de Faces of Evil |
| Zelda's Adventure: 4 módulos; 2 `Prog`, 1 `Subr`, 1 tipo não rotulado pelo relatório; inclui `cdi_bpsys`, `cdi_vsync` e `cdi_vsync_trap` | `data/private/inventory-adventure.log` | A semântica do módulo não rotulado ou sua compatibilidade com o emissor |
| Todos os módulos acima passaram paridade de cabeçalho e CRC no parser; os três volumes têm `CD-I ` no LBA 16 | Mesmos logs privados | Autenticidade, revisão comercial exata ou integridade de todos os setores do disco |

Os logs são privados e não devem entrar no Git. Nomes, contagens e tamanhos são metadados de investigação; não publicar bytes, desassemblagens ou código gerado dos jogos/BIOS. O padding observado no fim de algumas imagens requer investigação; isoladamente não prova corrupção.

## Meio óptico: Green Book Mode 2

O boletim técnico da OptImage, revisado com participação da Philips, descreve setores CD-i de 2.352 bytes: sincronismo de 12, cabeçalho de 4 e subcabeçalho de 8. Form 1 contém 2.048 bytes úteis mais EDC/ECC; Form 2 contém 2.324 bytes úteis, sem ECC, e campo final de 4 bytes reservado/EDC opcional. O subcabeçalho identifica arquivo, canal, codificação e flags de submodo; setores são entregues a 75/s. [OptImage, pp. 9–10](https://icdia.co.uk/authoring/cdi_standards.pdf).

Consequência para este projeto: preservar CUE, ordem dos setores, fronteiras de faixas, índices, subcabeçalhos e interleaving. Uma conversão cega para ISO de 2.048 bytes pode descartar informação necessária a áudio/vídeo. Detectar formatos efetivos, não inferi-los pela extensão. Inventário de arquivos e acesso a setores são camadas distintas.

O parser do `cdirecomp` auditado limita extensões, rejeita certas alocações ISO intercaladas/múltiplas e lê módulos dentro de arquivos; substitui setores Form 2 por zeros nessa leitura específica de Form 1. Isso é uma estratégia de inventário de código, não um extrator completo de cinematics. Conferir cada disco contra esses limites antes de confiar em uma ausência no relatório. [Fonte auditada, `disc_parser.c`](https://github.com/mstan/cdirecomp/blob/f3c8d579efb11d5a33c6bc7c935dfbced773e62e/recompiler/src/disc_parser.c).

## OS-9/CD-RTOS e código carregado em execução

A referência aplicável é o manual OS-9/68000 2.4, não assumir que APIs atuais de OS-9 são equivalentes ao CD-RTOS. Um módulo tem cabeçalho, corpo e CRC de 24 bits. O identificador `0x4AFC` sozinho não basta: validar tamanho, paridade, CRC, tipo/linguagem e offsets. Existem módulos de dados e descritores, além de programas. O manual exige código reentrante e independente da posição. `M$Exec` é relativo ao módulo; `M$IData` e `M$IRefs` descrevem inicialização de dados e ajuste de ponteiros efetuado por `F$Fork`. Não tratar todo carregamento como relocação arbitrária de instruções. [Manual 2.4, cap. 1, pp. 7–15](https://www.icdia.co.uk/microware/tech/tech_1.pdf).

`F$Load` lê um ou mais módulos do arquivo, valida-os, adiciona-os ao diretório e liga o primeiro. `F$Link` busca nome/tipo/linguagem no diretório e retorna ponteiros de módulo e entrada, incrementando o contador de ligações. `F$UnLink`/`F$UnLoad` reduzem esse contador e podem liberar memória; há regras para grupos e módulos em uso. [Chamadas de sistema 2.4, pp. 41–42 e 69–70](https://www.icdia.co.uk/microware/tech/tech_call_1.pdf).

Proposta: recompilar antecipadamente cada imagem executável identificada e resolver em execução `(identidade do módulo, offset)` para função nativa. A identidade deve incluir hash integral e tamanho; nome não distingue revisões nem módulos diferentes chamados `cdi_zelda`. Base e instância carregada pertencem ao estado convidado. Escrita sobre código, descarregamento ou reutilização da região invalida a associação antes da próxima instrução. Chamadas indiretas, interrupções e retornos de traps precisam de entradas de retomada verificadas. Registrar lacunas em vez de apontar para uma função aproximada.

O upstream observa escritas reais em RAM para associar imagens a código estático e não intercepta `F$Load`/`F$Link`. É referência de desenho a avaliar sob sua licença, não uma promessa de suporte aos módulos Zelda. [Fonte auditada, `cdi_native.c`](https://github.com/mstan/cdirecomp/blob/f3c8d579efb11d5a33c6bc7c935dfbced773e62e/runner/src/cdi_native.c).

## Componentes e fronteiras

```mermaid
flowchart LR
  A[Disco e BIOS locais privados] --> B[Validação e inventário]
  B --> C[680x0: descoberta e análise de fluxo]
  C --> D[C gerado privado e compilador do host]
  D --> E[Executável nativo]
  A --> F[Serviço de setores e dados originais]
  F --> E
  E <--> G[Estado CPU, memória, traps e tempo convidado]
  G <--> H[Modelos de vídeo, áudio, CDIC e entrada]
  E --> I[Apresentação e mod opcional PT-BR]
```

| Camada proposta | Responsabilidade e critério |
| --- | --- |
| Entrada privada | Manifesto por revisão, hashes e formato; nenhuma alteração do original |
| Frontend 680x0 | Decodificar apenas ISA comprovada para o player; separar dados/código, flags, exceções, endianness e acessos desalinhados; não presumir 68020 completo |
| Descoberta de funções | Entradas de cabeçalhos, tabelas e destinos indiretos comprovados; evidência por offset; nunca classificar automaticamente todo byte como instrução |
| Emissor e compilação | C/C++ portátil compilado antes da execução para arm64/x86-64; mesmas semânticas convidadas; hashes das entradas e versão das ferramentas no relatório |
| Runtime de CPU/OS | Registradores, pilhas usuário/supervisor, exceções/traps, interrupções e despacho de módulos; inicialmente preferir CD-RTOS recompilado ao desenvolvimento de HLE de chamadas sem evidência |
| Runtime de hardware | Barramento, RAM, temporizadores/DMA/UART do SCC68070, vídeo MCD212, CDIC/áudio, slave/entrada e NVRAM conforme player escolhido; erros explícitos em registrador ou operação desconhecida |
| Host | Janela, áudio e controle atrás de adaptadores portáveis; tempo de simulação separado do relógio e taxa de apresentação do host |
| Mod | Consulta opcional após eventos de apresentação identificados; ver [LOCALIZATION.md](LOCALIZATION.md) |

O driver MAME consultado instancia SCC68070 e MCD212 e conecta CDIC, slave e NVRAM. Seu próprio status registra lacunas no hardware e ajustes de timing. Portanto, comparação com MAME é evidência útil, mas não prova absoluta do comportamento do console. Fixar versão, player, BIOS, PAL/NTSC, entradas e estado inicial para cada comparação. [Driver CD-i](https://github.com/mamedev/mame/blob/master/src/mame/philips/cdi.cpp), [CDIC](https://github.com/mamedev/mame/blob/master/src/mame/philips/cdicdic.cpp), [MCD212](https://github.com/mamedev/mame/blob/master/src/mame/philips/mcd212.cpp).

## Recompilação estática e cobertura verificável

Um executável que apenas abre um emulador continua sendo um wrapper. Nesta proposta, instruções dos módulos/BIOS são convertidas antes da execução e compiladas pelo compilador do host; hardware ainda exige modelos de compatibilidade. Carregamento dinâmico de módulos convidados não implica recompilação JIT: o código nativo pode já estar compilado e ser associado à base carregada.

Interpretação é permitida como instrumento de pesquisa, sempre identificável e contabilizada. Uma tela de título não comprova cobertura. Para cada cenário fixo, publicar um resumo sem material protegido:

- Registrar revisão/hash do disco e BIOS, versão das ferramentas, configuração do player, duração e sequência de entradas no relatório privado. Resumos públicos devem omitir hashes da mídia e traces.
- Contagens de instruções convidadas executadas por código recompilado e pelo intérprete, separadas entre jogo e BIOS/OS; cobertura dinâmica = `nativas / (nativas + interpretadas)`.
- PCs únicos por `(hash do módulo, offset)` em cada modo, faltas de despacho, identidades rejeitadas, invalidações e falhas desconhecidas.
- Total de bytes/entradas emitidos em relação ao código identificado, explicitando que código ainda não identificado é um denominador desconhecido.
- Frames/estado/áudio comparados, primeira divergência e limites de qualquer oráculo; registros descartados ou overflow tornam a medição inconclusiva.

As contagens devem medir instruções convidadas em ambos os caminhos; contagem de chamadas ao dispatcher, funções emitidas ou tempo de CPU do host não substitui essa razão. Baselines, traces e C gerado permanecem privados; fixtures sintéticas autorais podem ser versionadas.

Antes de trabalho extenso: teste sintético de duas instâncias do mesmo módulo em bases diferentes, chamada indireta, trap/retorno, invalidação por escrita e recarga de outra identidade. O primeiro teste real de Faces of Evil deve registrar a primeira entrada nativa de `cdi_link` com hash/base/offset corretos e estado consistente com a referência; depois ampliar para título, início e primeiro movimento com entrada reproduzível. Não marcar nenhum desses gates como aprovado nesta fase.

## Investigação por título

| Jogo | Próxima investigação baseada no inventário | Hipótese que precisa ser testada |
| --- | --- | --- |
| Faces of Evil — prioridade | `cdi_link`, entradas indiretas e recursos acessados desde o boot até o primeiro movimento; papel de `cdi_bumper`; recursos fora de módulos | Quais operações de vídeo/áudio e quais módulos posteriores são efetivamente exigidos |
| Wand of Gamelon | Comparar metadados e fluxos com Faces, mantendo manifesto próprio; repetir os gates por revisão | Semelhanças de inventário podem permitir infraestrutura comum, mas não justificam compartilhar lógica por nome |
| Zelda's Adventure | Identificar o tipo numérico e entradas de `cdi_vsync_trap`, interface de `cdi_bpsys`, sincronização e formatos dos recursos | Pode exigir caminhos adicionais de trap/subrotina/timing e descoberta; nomes não comprovam sua função |

Não se concluiu quais codecs, fontes, tabelas de texto, imagens com palavras ou formatos de cinematics cada jogo usa. Nem suporte a MPEG/DVC nem a ausência dele está estabelecida por estes inventários.

## Referências, licenças e políticas consultadas

Consulta em 12/10/2026. Links de branches móveis devem ser fixados em commits antes de importar qualquer dependência. A revisão local de `cdirecomp` efetivamente auditada é `f3c8d579efb11d5a33c6bc7c935dfbced773e62e`.

| Referência | Uso nesta fase | Licença/política verificada |
| --- | --- | --- |
| [cdirecomp](https://github.com/mstan/cdirecomp) | Auditoria do parser, associação de módulos e desenho BIOS/runtime; suporte Zelda não validado | [Texto intitulado PolyForm Noncommercial 1.0.0, modificado](https://github.com/mstan/cdirecomp/blob/f3c8d579efb11d5a33c6bc7c935dfbced773e62e/LICENSE); diferenças registradas em [UPSTREAM_AUDIT.md](UPSTREAM_AUDIT.md); não presumir compatibilidade com uma licença permissiva/comercial nem relicenciar código copiado |
| [N64Recomp](https://github.com/N64Recomp/N64Recomp) | Exemplo de separação frontend/runtime, overlays e despacho; frontend MIPS não resolve 680x0 | [MIT](https://github.com/N64Recomp/N64Recomp/blob/main/LICENSE); [CONTRIBUTING](https://github.com/N64Recomp/N64Recomp/blob/main/CONTRIBUTING.md) proíbe código gerado por IA em contribuições |
| [Zelda64Recomp](https://github.com/Zelda64Recomp/Zelda64Recomp) | Referência de produto e organização de runtime/mods; não usar como base técnica CD-i | [COPYING GPL v3](https://github.com/Zelda64Recomp/Zelda64Recomp/blob/dev/COPYING); [CONTRIBUTING](https://github.com/Zelda64Recomp/Zelda64Recomp/blob/dev/CONTRIBUTING.md) proíbe código gerado por IA em contribuições |
| MAME | Referência independente de hardware, sujeito a limitações declaradas | Arquivos `cdi.cpp`, `cdicdic.cpp`, `mcd212.cpp` consultados declaram BSD-3-Clause; projeto agregado [GPL-2.0-or-later](https://github.com/mamedev/mame/blob/master/README.md). Conferir licença de cada arquivo e dependência antes de reutilização |
| Microware OS-9 2.4 | Semântica histórica de módulos e chamadas | [Distribuição autorizada pelo fornecedor no ICDIA](https://www.icdia.co.uk/microware/): copyright 1990–1994, todos os direitos reservados, publicação educacional; somente links e notas próprias neste repositório |
| OptImage Technical Bulletin 001, 1993 | Descrição primária dos formatos CD-i; não substitui o Green Book integral | [Documento](https://icdia.co.uk/authoring/cdi_standards.pdf), copyright OptImage, todos os direitos reservados; não redistribuído |

Nenhum código dessas referências foi incorporado às ferramentas próprias. O checkout de cdirecomp é uma referência local isolada. A escolha entre manter dependência separada sob os termos encontrados, pedir autorização adicional, contribuir ao cdirecomp ou implementar componentes próprios deve ser registrada em `DECISIONS.md` antes da implementação. As políticas de contribuição de N64Recomp/Zelda64Recomp serão respeitadas: este trabalho assistido por IA não será enviado como contribuição a esses projetos.
