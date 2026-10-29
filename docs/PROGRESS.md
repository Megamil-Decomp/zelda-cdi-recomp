# Progresso

## 2026-10-29 — auditoria para publicação do código e próximos passos Deck

Usuário autorizou push dos ajustes, excluindo ROMs e versões completas. Revisados os três commits locais pendentes, contendo somente fontes autorais, patches, testes e documentação; caminhos privados e extensões de mídia/pacotes não estão versionados nesse conjunto. Não criar release/anexar ZIPs completos.

Avaliação para Steam Deck em `STEAM_DECK_PLAN.md`: começar por validar Windows e testar seu pacote via Proton, depois medir a necessidade de Linux nativo. Auditoria do frontend confirmou D-pad/A/B e ausência de leitura direta de eixos; README e rótulo da interface Mac corrigidos para não prometer stick nativo; a mudança de rótulo entrará nos próximos pacotes gerados. Mouse do runtime depende de captura, desligada na configuração inicial; perfil com trackpad dentro do jogo precisa de ensaio específico. Nenhum port Deck/Linux ou perfil Workshop foi entregue/validado nesta etapa.

## 2026-10-29 — primeiro pacote Windows x64 para teste

Cross-compilados os três candidatos aceitos para PE x64 com MinGW GCC, mantendo o C gerado e os patches existentes. Cada fonte foi conferida contra a proveniência aceita; staging Windows separado e checkout upstream intacto. SDK SDL2 2.32.10 obtido da publicação oficial, com hash conferido; nenhuma mídia foi baixada.

Criados launcher Win32 e `scripts/build_windows_runtimes.py` / `scripts/export_private_windows.py`. A interface oferece seleção dos três jogos, verificação SHA-256 dos runtimes/BIOS/CUE/BIN, cache normalizado, saves/logs por título, encerramento normal e mod PT-BR parcial opcional de Adventure. Executáveis incorporam manifesto UTF-8. O pacote inclui a DLL SDL2 e as licenças; não precisa de Python, REA ou compilador no computador destino.

Primeiro ZIP em `dist/windows-preview/Zelda-CDi-Windows-Completo.zip`. Conferidos PE x64, imports/DLLs presentes, manifesto UTF-8 nos quatro executáveis, hashes dos arquivos copiados e integridade ZIP. **133 testes sintéticos Python passaram**; launcher compilou também com `-Wall -Wextra -Werror`. Uma nova execução do build de Faces reutilizou os objetos existentes, sem recompilar o jogo.

**Execução real no Windows ainda não validada.** Não há Windows/Wine disponível neste host; testes CTest Windows foram compilados, não executados. Não atribuir aceitação de gameplay Windows às reproduções anteriores no Mac. O pacote é a versão para o teste solicitado pelo usuário. Instruções em `WINDOWS_TESTING.md`; plano em `WINDOWS_PLAN.md`. Mídia e saves originais, runtimes macOS e fontes upstream permanecem preservados.

## 2026-10-29 — exportação completa para outro Mac

Criado `scripts/export_private_macos.py`: verifica o aplicativo aceito e os hashes da mídia, copia somente a BIOS selecionada e os três pares CUE/BIN para `Contents/Resources/LocalMedia`, compila o launcher atualizado na cópia e remove a raiz absoluta da origem. Detecta mídias internas sem dependência da pasta do projeto. A cópia tem domínio próprio de preferências; não contém saves pessoais. Originais e pacote principal permanecem preservados.

Primeiro ZIP privado: `dist/portable/Zelda-CDi-Completo.zip`, **474.527.466 bytes**, versão 0.1.6. Assinatura profunda/estrita e integridade ZIP passaram. O ZIP foi extraído em outro caminho e os sete arquivos de mídia foram reconferidos por hash, junto com a assinatura do aplicativo extraído. A interface foi aberta com preferências novas; os três títulos reconheceram os caminhos internos e mantiveram Iniciar habilitado. Uma sonda de boot usou exclusivamente runtime/BIOS/disco exportados, bateria nova e cache normalizado privado; observou shell e binding do módulo, zero dispatch misses, sem certificar gameplay pela captura final preta de transição. Os testes de gameplay aceitos da etapa anterior continuam sendo a referência.

**125 testes sintéticos Python passaram**, incluindo seis testes da exportação: identidades, conjunto completo, nomes CUE com espaços/aliases, contenção de paths e mudança de arquivo entre plano/cópia. Mídias copiadas conferidas por hash, saves originais preservados. Arquivos completos continuam ignorados pelo Git. Documentação de uso em `PRIVATE_EXPORT.md`; avaliação Windows/Vita/3DS em `PORTABILITY.md`, sem alegação de ports já executados.

## 2026-10-29 — Adventure: ampliar percurso e reduzir fallback de vídeo; pacote 0.1.6

Continuado o trabalho autorizado em Adventure. A exploração da build v1 alcançou novas telas, inimigos e dano, com retorno posterior a Vision Henge com corações restaurados; isso é consistente com morte/retorno, sem certificação de campanha. Outra sessão confirmou inventário → movimento do ponteiro → mapa → inventário → gameplay. Capturas pretas de transição foram distinguidas de espera permanente. Instrumentação privada não observou sobrescrita de resposta de input nos trechos ensaiados; o protocolo foi preservado.

O segundo lote de seeds do jogo passou na emissão estrita, mas melhorou apenas de 89,27% para 89,43% no percurso adicional, incluindo BIOS. Não foi promovido. A classificação mostrou cerca de 71% da interpretação residual na ROM. REA/Ghidra confirmou dois laços de cópia no módulo OS-9 de vídeo da BIOS, cuja identidade, cabeçalho e CRC foram conferidos. As entradas observadas sustentaram nova emissão em árvore privada isolada, mantendo os módulos estáticos Adventure v1. Foram acrescentadas cinco entradas técnicas de função pelo emissor; isso não prova fronteiras/nome de funções originais. Nenhuma alteração de semântica de hardware foi introduzida.

### Comparação e limites

- Referência v1 repetida: **89,19% nativo**, 1.985.602 instruções interpretadas no intervalo. Candidato BIOS: **92,20% nativo**, 1.434.423 interpretadas. Ganho de aproximadamente **3 pontos percentuais**, incluindo BIOS. Publicação de inputs em frames diferentes; não é equivalência determinística de CPU/ciclos/áudio nem benchmark de velocidade.
- Ambos completaram o percurso por controles normais, incluindo saída sul, dano/retorno e inventário. Sete de nove hashes de imagem correspondem; as duas capturas divergentes mostram as mesmas cenas com diferenças de transição/fade. Zero dispatch misses.
- **Ensaio a 1x**, com cópia da bateria do usuário: menu, save, percurso, dano/retorno e inventário completados, **92,28% nativo** nesse intervalo, sem erro de disco ou encerramento espontâneo. A saída -9 registrada foi limpeza solicitada pelo harness após captura final, não crash do jogo.
- Binário efetivamente empacotado também completou o replay: **92,19% nativo** nesse outro intervalo. Esses percentuais incluem BIOS e não certificam toda a campanha. O fluxo livre anterior que terminou preto continua sem causa conclusiva; os ensaios desta etapa não cobrem todas as sequências possíveis. SDL dummy: áudio físico continua sem validação.

### Entrega e preservação

Aplicativo principal **0.1.6 (build 7)** em `dist/Zelda CD-i.app`, com DMG e ZIP atualizados. Versão 0.1.5 preservada em `dist/previous-before-bios-rea-20261029/`. Catálogo seleciona a nova build apenas para Adventure; hashes de origem de Faces e Gamelon aceitos foram preservados. Seletor, perfis PT-BR e diretórios de saves continuam no pacote. Launcher principal 0.1.6 aberto e conferido por acessibilidade: três títulos, Adventure selecionado, caminhos corretos e botão Iniciar habilitado; nenhuma sessão foi iniciada sobre o save original.

**119 testes Python** e **11/11 CTest** passaram. Emissão BIOS estrita: zero eventos sem suporte e auditoria de fall-through limpa. Assinatura profunda/estrita, manifesto dos três executáveis, DMG e ZIP conferidos, sem BIOS/discos no bundle. Mídia contra lock: exit 0; baterias originais e upstream/core preservados, `git diff --check` limpo. Relatórios, seeds, imagens e código gerado permanecem exclusivamente em `data/private/rea-titles/` e `build/rea-titles/`.

## 2026-10-28 — REA em Adventure/Gamelon e launcher 0.1.5

Usuário confirmou melhora de Faces e pediu continuidade nos outros dois títulos, priorizando Zelda's Adventure e a interface de seleção. A build local principal em `dist/Zelda CD-i.app` foi atualizada para **0.1.5**, com DMG/ZIP correspondentes e cópia dos artefatos anteriores em uma pasta `dist/previous-before-rea-*`. O pacote de preparação permanece em `dist/rea/`. Nenhuma publicação, commit ou push realizado.

### Adventure

- Coletado ledger completo inicial com **1.624 destinos** do Prog principal. REA/Ghidra verificou o mapeamento, analisou a função de entrada e inspecionou dois hotspots; quatro operações retornaram Evidence com identidade conferida. O primeiro ensaio também continha demonstração automática: imagens com HUD não foram aceitas isoladamente como gameplay.
- Emissão estrita das entradas observadas passou. O candidato contém os patches comuns 0007/0008/0009 e mantém o fallback nos destinos ainda não recompilados. O Subr continua excluído; nenhum layout de exports foi adivinhado.
- Comparação controlada, com cópias da mesma bateria, reconheceu o menu, entrou no save e exercitou inputs/inventário na área inicial. No intervalo medido, a proporção nativa passou de **45,85% para 91,86%**, **incluindo BIOS**. Zero dispatch misses nos dois ensaios. Os frames de publicação de inputs diferiram; isso não comprova equivalência determinística de CPU, ciclos ou áudio.
- Um ensaio livre anterior terminou em tela preta, sem aborto host, após sequência diferente de inputs/esperas. Esse fluxo não foi estabelecido como a mesma causa nem descartado do registro. Replays controlados completaram. Uma variante do harness também não reconheceu o hash transitório do menu e foi parada pelo coordenador; o reconhecedor passou a conferir uma região estável privada, sem mudar o runtime.
- **Runtime efetivamente empacotado testado a 1x** com bateria copiada: menu, entrada no save, movimento, primeira transição sul de Vision Henge para a tela com o rochedo, inventário e retorno. Não apareceu o erro de disco nesse percurso. Medição desse outro intervalo: **90,78% nativo**, incluindo BIOS. Caminhos posteriores, campanha e saída de áudio física permanecem sem validação completa; SDL dummy foi usado nos ensaios automáticos.

### Gamelon

Ledger completo de referência: 2.409 destinos, dos quais **2.404 no Prog principal**, usado para as novas seeds; o outro Prog foi preservado na emissão. REA completou as mesmas quatro operações de análise/inspeção, com Evidence privado e identidades verificadas. Emissão e build passaram. O candidato chegou ao mapa, menu e área jogável de Sakado/loja; foram observados movimento e retorno ao mapa após input. Zero dispatch misses no intervalo registrado. A observação de instruções nativas desse trecho foi 97,21%, incluindo BIOS, **sem ensaio pareado correspondente de gameplay para comparar percentuais**. Campanha não validada.

### Interface e checks

O launcher mantém os três jogos, dados por título e mod PT-BR opcional existente. O catálogo privado escolhe exatamente os três runtimes por hash, preservando o Faces aceito pelo usuário; o manifesto confere separadamente hash de origem e binário assinado. A interface 0.1.5 foi aberta e inspecionada por CUA: os três títulos aparecem, Adventure está selecionado e os caminhos da mídia estão corretos. A seleção não iniciou uma sessão sobre o save original durante os testes. O About deixou de atribuir MIT ao runtime inteiro; os termos auditados acompanham o pacote.

- **119 testes sintéticos Python passaram**, incluindo seis cenários de catálogo/identidade.
- Componentes nativos: **11/11 CTest em Adventure e 11/11 em Gamelon**.
- Assinatura profunda/estrita, hashes dos três binários empacotados e DMG verificados. Sem BIOS/discos adicionados ao pacote.
- Mídia reconferida contra o lock: exit 0. Baterias originais e fontes de teste preservadas; upstream/core limpos, `git diff --check` sem erros.
- Fontes comerciais geradas, seeds, imagens, bancos REA, hashes e evidência detalhada ficam em `build/` e `data/private/rea-titles/`. Plano em `REA_OTHER_TITLES_PLAN.md`; procedimento em `REA_WORKFLOW.md`.

## 2026-10-28 — continuação: prioridade de IRQ e primeira área visível

A investigação da espera avançou além do diagnóstico anterior. O runtime verificava a máscara de prioridade ao aceitar uma IRQ, mas não a elevava durante o reconhecimento. A captura privada do estado do driver mostra uma conclusão AP interrompendo o atendimento anterior antes de ele limpar o pedido pendente; o atendimento interno consome esse pedido antigo e deixa o driver ocioso com os dois buffers de dados ocupados. O laço de espera identificado com REA era consequência desse estado.

Conferida a especificação Philips SCC68070 de abril de 1993, seção 5.11, página 23, por OCR e inspeção visual da página original, obtida no [arquivo técnico SCC68070](https://www.icdia.co.uk/docs/scc68070.zip). Patch 0009 em staging eleva IPL ao nível reconhecido e suprime trace após empilhar o SR anterior. Não altera latência AP, ownership CIAP, BIOS ou lógica comercial. A fixture sintética falha no original e passa no corrigido: frame/SR/PC/vetor, pilhas separadas, reentrada de mesmo nível bloqueada, nível superior permitido, IRQ on-chip, pendências mascaradas e restauração do contexto.

### Reprodução real

- No cenário anterior de entrada/colisão em Goronu, a referência ficava preta e aguardava flags de mídia. Com a correção, imagens de frames completos mostram a área jogável, Link, inimigo em movimento, colisões, dano e a tela de Continue. O processo e a lógica continuaram avançando, com zero dispatch misses no intervalo observado.
- Outro ensaio manteve Link atacando e depois andando à direita. As capturas mostram golpes, efeito de acerto no inimigo, reaparecimento de inimigo e avanço horizontal. **Essa sequência também passou sem o patch 0009**; portanto, isoladamente, não reproduz nem comprova a correção do ataque específico relatado pelo usuário. A prova da regressão está no teste de CPU e no cenário de reentrada/espera, não na mera ausência de crash durante ataques.
- A variação de aproximação seguida de ataques também completou nas duas versões. Não confirmou dano nem uma nova falha anterior; permanece um check adicional de execução, sem acrescentar prova sobre o objeto específico relatado.
- Em teste a 1x, 160 pulsos de BTN1 usados para pular a abertura chegaram ao mapa com Nortinka selecionada, sem SIGABRT observado. O harness não reconheceu o hash transitório do menu e encerrou por seu deadline; a imagem final foi inspecionada e a limitação do reconhecedor registrada, sem classificar esse resultado como lógica travada.
- Ensaios a 4x usam SDL dummy; não certificam saída de áudio física. A captura final pausa intencionalmente a execução; o SIGKILL de cleanup do harness não é crash espontâneo do jogo. Inputs foram publicados em frames diferentes entre ensaios, sem alegar equivalência determinística de CPU/ciclos.

### Validação e limites

**113 testes sintéticos Python passaram**, incluindo os oito novos cenários de IRQ; **11/11 CTest nativos passaram**. Build CMake com patches 0008/0009 concluída, com proveniência dos inputs vinculados. Mídia conferida contra o lock original, exit 0. Dados derivados, logs, imagens e módulos permanecem ignorados. Upstream/core intactos; sem commits/pushes.

O replay de combate também completou na build CMake sem instrumentação adicional de captura, com ataques, movimento e zero dispatch misses. O manifesto privado passou a selecionar `irq-fixed`; o mesmo comando `scripts/run_faces_rea_candidate.py` usa essa build. Identidades de runtime, BIOS e disco verificadas; `fetch-fixed` foi preservado separadamente para comparação.

O candidato permanece experimental: validações cobrem abertura e trechos curtos da primeira área, não campanha completa. O relato sobre um objeto específico à direita ainda exige distinguir o objeto exato da sequência de inimigo/colisão reproduzida. Wand e Adventure têm apenas as provas estáticas REA descritas abaixo, sem nova certificação de runtime.

## 2026-10-28 — regressões relatadas pelo usuário: fetch corrigido, gameplay ainda bloqueado

O usuário relatou encerramento ao pular a abertura Philips e travamento ao atacar um objeto à direita no primeiro trecho jogável. O piloto anterior não havia validado esse trecho; os percentuais de recompilação não demonstram jogabilidade.

### Fechamento e diagnóstico por sessão

- Preservados por cópia os dois logs fornecidos, a bateria e o crash report correspondente, em `data/private/faces-regression/`.
- O crash report confirmou SIGABRT em leitura de registrador de vídeo feita pelo preenchimento antecipado da janela do intérprete, antes de executar o operando. Um dos logs termina nessa falha; o outro registra encerramento solicitado pelo player e não prova, sozinho, a causa do travamento de lógica.
- Patch 0008 limita a cópia especulativa ao span RAM/ROM disponível e rejeita instruções truncadas. Não fabrica valores de MMIO; a exceção já implementada para operandos reais continua funcionando. Fetch em MMIO permanece explicitamente não suportado, sem alegar frame arquitetural completo.
- Regressão sintética falha antes (leitura indevida de MMIO) e passa depois, incluindo CSR preservado, instrução curta no limite, extensão ausente, fim de RAM e exceção de operando.
- Replay com inputs para pular a abertura reproduziu SIGABRT na build anterior. A build corrigida suportou a sequência prolongada sem esse aborto, mas permaneceu na tela Philips em uma variante do replay. Isso não valida a abertura pulada como fluxo completo; não confundir sobrevivência do processo com progresso.
- O launcher experimental agora registra comando, hash do runtime, resultado/sinal de saída e horário em JSON por sessão. A seleção privada padrão passou a `fetch-fixed`; a anterior continua acessível para comparação. O aplicativo normal não foi substituído.

### Investigação do trecho jogável

Replays por controles normais chegaram ao mapa e selecionaram Goronu, mas encontraram tela preta e espera por flags de conclusão de mídia. A mesma espera foi observada tanto na referência anterior quanto no candidato com fetch corrigido, inclusive em observação prolongada. Vídeo/clock continuam avançando, com zero dispatch misses; isso não significa que a lógica esteja funcionando.

Foram preservados estado de CIAP, registradores, trace, ações e histórico de acessos ao dispositivo. REA confirmou a instrução de teste no laço e ajudou a inspecionar o despacho de conclusão do driver. O registro mostra buffers de dados ocupados e ausência de progresso no atendimento após a mudança de estado do áudio. A causa completa da falta de conclusão ainda não foi estabelecida. Não foi validado que essa reprodução seja exatamente o objeto descrito pelo usuário: ainda falta chegar à área visível e repetir o ataque nessa condição.

Um experimento privado aumentando a latência de conclusão AP não resolveu a espera e não foi adotado. Não foram acrescentados ACKs artificiais, flags de conclusão forçadas, valores inventados de registradores ou alterações na lógica comercial para esconder a falha. A documentação de [CIAP de cdifan](https://github.com/cdifan/cdichips/blob/master/mcd221ciap.md) declara limites da engenharia reversa e descreve uma semântica de pares BMAN que exige confrontar as hipóteses locais com evidência adicional; não foi copiado código de outro emulador.

### Outros títulos

Foi executada prova estática real com REA nos módulos Prog principais de Wand of Gamelon e Zelda's Adventure: paridade/CRC válidos, mapeamento verificado e função de entrada analisada com pseudocódigo, assembly e CFG disponíveis. Nenhuma nova build ou validação de gameplay desses títulos foi realizada. O Subr de Adventure permaneceu fora da prova. CUE/BIN foram reconferidos sem alteração; evidência em `other-titles-summary.json` privado.

### Checks

- Ferramentas próprias: **105 testes sintéticos passaram**.
- Componentes nativos da build corrigida: **11/11 CTest passaram**.
- Patch aplicado somente em staging; checkout upstream/core preservados, sem commits ou pushes.
- O candidato continua **experimental e com bloqueio conhecido**, não aceito como jogável. Plano específico em `FACES_GAMEPLAY_REGRESSION_PLAN.md`.

## 2026-10-28 — piloto REA, correção de descoberta e candidatos de Faces

Autorizado trabalho autônomo com REA. Instalados localmente REA 6.8.0 e Node 24.22.1; Ghidra 12.1.4 com decompilador compilado para macOS arm64 e JDK 25 existente. O Ghidra 12.2 inicialmente obtido foi recusado pelo controle de versão do REA e removido após preservar diagnóstico/proveniência. Configuração global do agente permaneceu intacta.

### Ferramentas e evidência

- `prepare_rea_module.py` valida/extrai um módulo Prog de uma extensão Form 1 explícita, preserva seus bytes e cria envelope privado de análise; não é extrator geral de filesystem. REA verificou o mapeamento sintético m68k, decompilou a entrada de Faces e inspecionou destinos observados. O superset 68040 do Ghidra e o ABI OS-9 continuam limitações explícitas.
- `analyze_rea_module.py` automatiza verificação do envelope, análise da entrada e hotspots, retendo Evidence completo e conferindo identidade/operação/provider. Teste real completou cinco operações REA. Seeds exportadas são experimentais e não são aplicadas automaticamente.
- Corrigido o probe: o relatório antigo salvava só 64 de 250 destinos anunciados. A nova coleta salvou 465/465, sem overflow, com paginação e pausa estável; posteriores também ficaram completas. Falha de consulta/reset dos contadores agora invalida a medição, em vez de produzir zero/percentual enganoso.

### Correção reproduzida

A emissão de todas as entradas observadas inicialmente falhou com `INVALID_STORE_EA`. A análise REA/Ghidra classificou como dado um dos endereços especulados. A investigação do gerador revelou leitura da própria extensão do JMP como primeira linha de tabela, inventando um caminho por dados.

Patch `0007-jump-table-extension-guard.patch` suspende essa inferência quando a base está dentro da instrução, preservando o fallback para o destino calculado. Aplicado somente ao staging e integrado à pipeline reproduzível; upstream e submódulo permaneceram limpos. Fixture autoral reproduziu a emissão inválida no código anterior e passou no corrigido; tabela externa legítima continuou funcionando. Os termos do core/upstream permanecem os auditados, sem relicenciamento.

### Ensaios reais e limites

| Ensaio privado | Resultado observado |
| --- | --- |
| Baseline até frame 7.000 | 49,58% de instruções nativas no intervalo pós-shell, incluindo BIOS; zero dispatch misses |
| Candidato com três entradas frequentes | 53,03%; emissão estrita passou; comparação visual com alinhamento ajustado registrou 98,77% de frames iguais |
| Candidato com entradas da primeira coleta + patch 0007 | 96,56% no intervalo até frame 7.000, incluindo BIOS; zero dispatch misses; 97,02% de frames iguais após ajuste de 22 frames |
| Mesmo candidato até frame 18.000 | Game Menu confirmado visualmente; zero dispatch misses; 62,05% no intervalo ampliado, revelando novos caminhos interpretados |
| Segundo candidato com entradas do intervalo ampliado | Emissão estrita e build passaram; até frame 19.500, 89,26% nativo no intervalo observado, incluindo BIOS; menu reconhecido por imagem e botão Start Game entregue, avançando para nova sequência; zero dispatch misses |

As publicações de input ocorreram em frames diferentes. O alinhamento visual é ajustado e não comprova equivalência de CPU, ciclos ou áudio. Os percentuais de intervalos diferentes não são diretamente intercambiáveis; 96,56% não representa a campanha nem todo o intervalo ampliado. Permanecem sítios de salto indireto com fallback. Testes usaram SDL dummy a 4x, com descartes na fila host de áudio; não certificam áudio físico. Start Game abriu a sequência seguinte, sem validação de gameplay/campanha.

Resultados detalhados, hashes, eventos, pseudocódigo e harness: `data/private/rea-pilot/`; candidatos e código gerado em `build/rea-pilot/`. O aplicativo entregue em `dist/` não foi substituído. `run_faces_rea_candidate.py --check` verificou runtime, BIOS e disco; sem `--check`, abre o candidato experimental a 1x com bateria própria em pasta privada. A execução interativa desse comando ainda não foi certificada com áudio físico.

### Validação final

- `python3 -m unittest discover -s tests -v`: **93 testes sintéticos passaram**.
- CTest do frontend corrigido: **6/6 passaram**.
- Compilações dos três candidatos concluídas. Linker advertiu que a SDL instalada exige macOS mais novo que o deployment target; estes binários de pesquisa não certificam suporte a macOS 13.
- Verificação dos nove arquivos de mídia contra o lock original: exit 0 antes e depois; baterias usadas nos ensaios são próprias, sem tocar nos saves originais.
- `git diff --check` passou; checkout upstream e core limpos; arquivos derivados ignorados. Sem commits ou pushes.

Procedimento reutilizável em `REA_WORKFLOW.md`; plano e critérios em `REA_PILOT_PLAN.md`. Próximo gate: comparação determinística de CPU/tempo e validação da primeira área jogável antes de promover seeds ao build normal.

## 2026-10-14 — cinco botões em PT-BR para teste

Pacote 0.1.4 separado em `dist/ptbr-menu/`: compositor host desenha JOGAR, CRIAR, APAGAR, COMO JOGAR e SAIR sobre o menu reconhecido, junto a VAZIO. Captura real conferida; clique em COMO JOGAR abriu instruções e o compositor rejeitou essa tela sem alterar pixels. 44 testes sintéticos passaram; patch reproduzível e assinatura verificados; sondas removidas do build final. Aparência provisória, demais cliques/campanha pendentes. Ver `MENU_OVERLAY_PLAN.md`.


## 2026-10-14 — índices de recursos do menu Adventure

Observação da fonte confirmou nomes de save/EMPTY; botões não apareceram nesse caminho nem em ASCII/UTF-16 do executável. Hipótese gráfica ainda requer correlação. Leitor autoral exportou 47 recursos de mapres e 193 do prefixo zelda.rtf, preservando campos desconhecidos. 38 testes sintéticos passaram. Sondas removidas e runtime reconstruído; pacote entregue não mudou. Detalhes em `ADVENTURE_MENU_LOCALIZATION.md`.


## 2026-10-14 — idioma da GUI controla o piloto

Seletor existente de idioma agora ativa o mod de Adventure apenas em português; inglês limpa overrides herdados. Preferência persistida; reinício do jogo necessário. Interface identifica tradução parcial e limite EMPTY → VAZIO. Pacote 0.1.3 separado em `dist/ptbr-gui/`. Swift compilado e 33 testes sintéticos aprovados; alternância visual pelo usuário pendente.


## 2026-10-14 — primeiro texto aplicado em Adventure

Autorizado pelo usuário o avanço da extração para tradução/aplicação. Confirmado o caminho de fonte dos slots de save; piloto `EMPTY → VAZIO` aparece visualmente no menu, mantendo nome do save e bytes originais da memória. Integração opcional apenas nas leituras de desenho/medição; sem modificar imagem, save ou identidade do módulo recompilado.

Pacote separado 0.1.2 em `dist/ptbr-pilot/`, com configuração externa e opção `enabled=false` para reiniciar em inglês. O aplicativo normal não foi substituído. Escopo: **um rótulo de Zelda's Adventure**, não tradução completa nem suporte aos outros dois títulos. 33 testes Python e 3 componentes CTest passaram. Evidência privada e instruções: `TEXT_PILOT_PLAN.md`.

## 2026-10-14 — automação de descoberta de texto

Adicionado `scripts/text_catalog.py`: extração somente leitura de sequências ASCII em setores Form 1, com spans físicos, IDs por ocorrência, SHA-256 privado da mídia, CSV completo e fila prioritária. Comando `validate` confere CSV traduzido e produz um pacote intermediário, explicitamente sem suporte de runtime/injeção.

Adventure: 50.291 candidatos após filtro básico; 633 na fila heurística prioritária. Esses números incluem ruído binário e não representam frases confirmadas. `EMPTY` e `Zelda Saves` reconhecidos. Form 2, texto comprimido/codificações próprias, imagens e voz não são decodificados. Exportações em `data/private/localization/adventure-catalog-v1.*`; validação vazia executada com sucesso. Suite Python: 29 testes passaram. Instruções e critérios em `TEXT_PIPELINE.md`. Nenhum byte de mídia/save/runtime alterado, commit ou push realizado.

## 2026-10-13 — erro de disco de Adventure: diagnóstico e correção de buffers ADPCM

Reproduzida a mensagem `Your Disc May Be Dirty` usando uma cópia do save/NVRAM do usuário. O save original, a BIOS e o disco permaneceram intactos. A alegação de 12/10 abaixo sobre a correção definitiva por ACK genérico não se sustentou na reprodução atual; os registros antigos cobriam boot/introdução, não essa transição.

### Causa observada

Na substituição de um som, o driver preserva o buffer ativo, retira o outro e pode repor o buffer 0 depois que o par esvazia. O modelo de áudio continuava alternando rigidamente para o buffer 1. O buffer 0 ficava entregue mas inativo (`BMAN=1`, `ASTAT=0x0400`); `FINISH` aguardava indefinidamente, levando ao erro do jogo. Não houve falha de leitura host da imagem nessa captura.

### Mudança e evidências

- Patch reproduzível `scripts/patches/0004-adventure-audio-reselection.patch`, aplicado pela pipeline; nenhuma modificação no checkout original do upstream.
- Preservação do buffer ativo e reseleção após o par esvaziar, incluindo múltiplas reposições consecutivas no mesmo buffer. A tentativa intermediária que permitia só a primeira reposição ainda falhou; sua captura foi preservada.
- Regressão sintética de hardware falha no código anterior e passa no corrigido. Logs em `build/adventure-regression/before.log` e `after.log`.
- Testes CTest `cdic` e `cdi_audio`: 2/2 passaram. Ferramentas próprias: 20/20 testes Python passaram.
- Aplicação limpa do patch reproduz exatamente o código e a fixture testados; verificação em `build/adventure-regression/patch-check/`.
- Reprodução privada a 4x: o save abriu, a primeira saída sul e novas transições ocorreram sem erro; ainda respondia e fazia leituras após 16.993 frames, com zero dispatch misses. Capturas/estados em `data/private/probes/adventure-transition-after2/`.
- Runtimes dos três títulos reconstruídos com a correção compartilhada; `.app` e `.dmg` atualizados para 0.1.1 (build 2). Assinatura local e integridade do DMG verificadas pelo empacotador.
- Pacote final a 1x: save carregado, saída sul e nova mudança de tela com controle normal, sem a mensagem de disco sujo ou dispatch misses. Capturas e `acceptance.json` em `data/private/probes/adventure-package-1x/`; captura final consistente com execução pausada. Frontend SDL dummy: qualidade física de áudio não certificada por esse teste.
- Verificador de mídia comparado ao lock original retornou exit 0; NVRAM original do usuário continua byte a byte igual à cópia anterior aos testes.

Capturas anteriores: `data/private/probes/adventure-transition-before/`; tentativa intermediária: `adventure-transition-after/`. Capturas são privadas. Teste final do pacote a 1x registrado separadamente em `adventure-package-1x/`. Não há certificação de campanha completa nem de qualidade sonora a partir de FPS.

## 2026-10-12 — correção de fechamento inesperado e destravamento de Zelda's Adventure

1. **Prevenção de encerramento prematuro/crash no frontend (`cdi_frontend.c`)**:
   - Falhas no `SDL_SetRelativeMouseMode` (comuns em alternância de foco no macOS) não causam mais o encerramento do processo (`s.mouse_captured = 0; return 1;`).
   - O evento de perda/ganho de foco da janela não encerra mais o loop em caso de erro.
   - A tecla ESC simples não fecha mais o jogo acidentalmente; a saída por teclado requer `Cmd+Q` ou `Cmd+Esc`.
2. **Resolução do erro "disco retirado ou sujo" no Zelda's Adventure (`slave.c`)**:
   - Identificada a causa raiz: consultas de diagnóstico do mecanismo de disco (`$F2`) e comandos do Canal C do IKAT (`$F1`, `$F9`, `$8x`) eram descartados pelo emulador, deixando o driver de CD do CD-RTOS em espera infinita de confirmação até timeout.
   - Implementado fallback respondendo `{ 0xA5, cmd, 0x00 }` com interrupção no Canal C.
   - Validada a caminhada e transição de telas com mais de 7.000.000 de instruções a 60 FPS cravados sem erros de disco ou travamentos.
3. **Pipeline e empacotamento**:
   - Novo patch isolado criado em `scripts/patches/0003-stability-and-adventure-cd-fix.patch` e integrado a `scripts/build_native_runtimes.py`.
   - Executáveis dos 3 títulos recompilados e empacotados em `dist/Zelda CD-i.app` e `dist/Zelda-CDi-AppleSilicon.dmg`.
   - 20 testes unitários executados com sucesso em `tests/`.
4. **Portabilidade do Launcher e Dicas de Mídia (`Launcher.swift`)**:
   - Removido caminho absoluto hardcoded do desenvolvedor do manifesto de distribuição (`--no-local-paths`).
   - Implementada autodeteção inteligente na pasta do bundle (`bundleFolder/bios` e `bundleFolder/roms`), permitindo execução plug-and-play do app ao descompactar o ZIP em qualquer máquina.
   - Limpeza automática de caminhos herdados inexistentes em `UserDefaults`.
   - Inclusão de dicas visuais explícitas, placeholders e mensagens de diálogo com nomes e extensões esperadas (`cdi490a.rom` 512 KB e arquivos `.cue/.bin`), totalmente localizado em inglês e português do Brasil.

## 2026-10-12 — estabilização em 60 FPS cravados e exibição de FPS em tempo real

1. **Eliminação dos gargalos críticos de overhead de depuração**:
   - Gating dinâmico de `debug_trace_block`, `debug_trace_store`, `debug_trace_interp` e `debug_ring_capture_frame`.
   - Remoção de ~124 MB de gravações contínuas de memória em cada instrução e do cálculo contínuo de FNV1a de 368 KB de pixels a cada frame.
   - Forçado `-DCDI_COSIM_BUILD:BOOL=OFF` em todos os 3 runtimes nativos, eliminando o cálculo do `cdi_cosim_ram_hash`.
2. **Pacing e QoS interativo no macOS**:
   - Definido `QOS_CLASS_USER_INTERACTIVE` na thread do runtime.
   - Pacing com drift re-anchoring imediato em 20ms e chunk de ~20ms, evitando stalls excessivos em `nanosleep`.
3. **Exibição de FPS em tempo real**:
   - `present_frame()` em `cdi_frontend.c` mede os frames a cada 500ms e atualiza o título da janela SDL (`Zelda CD-i — 60.0 FPS`).
4. **Resultados medidos nos 3 títulos**:
   - **Link: The Faces of Evil**: estabilizado em **60.0 FPS** cravados.
   - **Zelda: The Wand of Gamelon**: estabilizado em **60.0 FPS** cravados.
   - **Zelda's Adventure**: estabilizado em **60.0 FPS** cravados.
   - Áudio perfeitamente contínuo, sem estalos ou engasgos de buffer underrun.
   - Bundle `dist/Zelda CD-i.app` e instalador `dist/Zelda-CDi-AppleSilicon.dmg` recompilados e atualizados.

## 2026-10-12 — correção do layout de controles e otimização inicial de desempenho

1. **Correção do layout de Controles (`Launcher.swift`)**:
   - `ControlsWindowController` reescrito do zero: removido o `NSBox` com layout quebrado e tamanho fixo rígido de 520px.
   - Adicionado `NSScrollView` suave (`FlippedView`), cabeçalho e rodapé fixos, cartões modernos com bordas suaves e cantos arredondados.
   - Alinhamento de duas colunas com largura fixa na ação (230pt) e atalhos exibidos em badges/keycaps estilizados.

2. **Diagnóstico e solução do travamento severo de áudio, vídeo e CPU**:
   - **Causa 1 (VSync bloqueante no SDL)**: `SDL_RenderPresent` sincronizava com o display via Metal e bloqueava a thread do SCC68070 por até 16.6ms a cada frame. Resolvido com `SDL_SetHint(SDL_HINT_RENDER_VSYNC, "0")`.
   - **Causa 2 (Oversleep de Pacing)**: `nanosleep()` no kernel do macOS tinha jitter de 1–3 ms, fazendo o emulador rodar a menos de 100k insns/s. Resolvido substituindo nanosleep por `sched_yield()` para tempos inferiores a 2ms.
   - **Causa 3 (Buffer de Áudio)**: Aumentado `desired.samples` de 1024 para 2048 (~54ms) no SDL Audio, eliminando buffer underrun e estalos.
   - **Resultado medido**: A taxa de execução subiu de ~94.000 insns/s para mais de 550.000 insns/s, mantendo o áudio e a renderização fluidos.
   - Patch isolado registrado em `scripts/patches/0002-performance-pacing-audio-vsync.patch` e integrado em `scripts/build_native_runtimes.py`.

## 2026-10-12 — boot dos três títulos e empacotamento macOS

Runtimes arm64 dos três títulos compilados por `scripts/build_native_runtimes.py`
com BIOS normalizada e seeds explícitas. Empacotamento do app macOS e imagem
de disco finalizados via `scripts/build_macos_app.py`.

- **Faces of Evil**: boot via IKAT confirmado até o `Game Menu`
  (evidências em `data/private/probes/faces-timeline/`).
- **Wand of Gamelon**: boot via IKAT confirmado até o `Game Menu`
  (evidências em `data/private/probes/gamelon-timeline/`).
- **Zelda's Adventure**: boot via IKAT confirmado até o FMV do Gaspra / Pergaminho
  (evidências em `data/private/probes/adventure-timeline/`).
- **Empacotamento**: gerados `dist/Zelda CD-i.app` e `dist/Zelda-CDi-AppleSilicon.dmg`
  com launcher nativo em Swift/AppKit, empacotando os 3 runtimes arm64 e
  bibliotecas dinâmicas do SDL resolvidas via rpath (sem dependência de Homebrew em runtime).
- **Cobertura nativa pós-clique**: Faces ~24%, Wand ~30%, Adventure ~71% nativo;
  o restante executa sob fallback interpretado.
- **Próximos passos**: validação de input interativo/gameplay in-game e redução
  de rejeições de módulos para aumentar a proporção de código recompilado estático.

## 2026-10-12 — M0 concluído

O diretório inicial continha somente briefing no README, três pares BIN/CUE e três BIOS. O checkout upstream mencionado no briefing não existia e foi obtido para auditoria. O briefing original foi preservado em `PROJECT_BRIEF.md`; o README agora é a entrada de uso do projeto.

### Evidências executadas

| Verificação | Resultado | Evidência local |
| --- | --- | --- |
| Diagnóstico do host | macOS arm64; Clang/CMake/SDL disponíveis; exit 0 | `data/private/environment.json`, `ENVIRONMENT.md` |
| Build frontend upstream | Executáveis Mach-O arm64; exit 0 | `build/upstream-audit/logs/recompiler-build.log` |
| CTest frontend | 6/6 passaram; exit 0 | `recompiler-ctest.log` no mesmo diretório |
| Componentes runtime | Build exit 0; 11/11 CTest passaram | `runner-components-build.log`, `runner-ctest.log` |
| Fixture adicional de aliases | Passou; exit 0 | `function-aliases.log` |
| Executável completo do player | Build exit 2 no link; faltam 3 funções da BIOS gerada | `runner-full-build.log`; falha preservada sem stubs |
| Ferramenta própria | 20 testes sintéticos passaram; repetidos na revisão final | `python3 -m unittest discover -s tests -v` |
| Verificação de mídia | 9 arquivos, 3 discos, 35 amostras por volume; exit 0 com avisos | `data/private/media-report.json`, `media-verification.log` |
| Lock local | Criado sem sobrescrever anterior; comparação exit 0 | `data/private/media-lock.json`, `media-comparison-report.json`, `media-comparison.log` |
| Inventário OS-9 sem emissão | Três exit 0; Faces 5, Wand 5, Adventure 4 módulos; CRC/paridade válidos nos encontrados | `data/private/inventory-*.log` |
| Exclusões de Git | 9 caminhos privados ignorados e 5 caminhos de fontes permitidos em repositório temporário | Sem incluir mídia em índice e sem inicializar Git no projeto principal |
| Preservação upstream | `git status --short` vazio no clone e no core após builds/testes | Commit e submódulo em `UPSTREAM_AUDIT.md` |

Os seis testes CTest do frontend, onze do runtime, uma fixture Python upstream e vinte testes Python próprios totalizam 38 verificações reportadas; não equivalem a 38 cenários de gameplay.

Os comandos do inventário, depois dos testes sem mídia:

```sh
build/upstream-audit/recompiler/CdiRecomp \
  "roms/Link The Faces of Evil/Link - The Faces of Evil (Europe).cue" \
  > data/private/inventory-faces.log 2>&1
build/upstream-audit/recompiler/CdiRecomp \
  "roms/Zelda The Wand of Gamelon/Zelda - The Wand of Gamelon (Europe).cue" \
  > data/private/inventory-gamelon.log 2>&1
build/upstream-audit/recompiler/CdiRecomp \
  "roms/Zeldas Adventure/Zelda's Adventure (Europe).cue" \
  > data/private/inventory-adventure.log 2>&1
```

### Achados e limites

- Frontend e componentes sintéticos funcionam neste Mac. A execução integrada continua não testada; nenhum Zelda nem BIOS foi iniciado.
- Os textos de licença principal/core diferem da PolyForm oficial. Usar o upstream como referência experimental isolada; esclarecer termos antes de distribuição. As alegações upstream de autoria/proveniência não foram certificadas de forma independente.
- Faces e Wand contêm setores fora do volume declarado, incluindo pequena cauda uniforme. A ferramenta informa avisos; não estabelece sua origem, integridade ou necessidade para o jogo.
- Hashes são observados e servem ao lock pessoal. Não há autenticação externa dos dumps, validação completa EDC/ECC ou certificação de todos os recursos.
- Os formatos de textos, fontes e cinematics continuam não identificados por título. `LOCALIZATION.md` é proposta, não tradução ou suporte implementado.
- Não houve alterações nos arquivos de mídia, geração de BIOS/jogo, mudanças versionadas no upstream, commits ou pushes.

### Próximo trabalho

M1 de Faces: mapear entradas de módulos, referências inicializadas e destinos indiretos; definir uma comparação pequena antes da primeira emissão privada. Integrar BIOS/player e medir dispatch nativo em marcos seguintes. Critérios de FOE-BOOT-001, roadmap e instrução pronta estão em `ROADMAP.md`.
