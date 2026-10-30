# Continuidade por outra IA

Este é o ponto de entrada para continuar sem o histórico do chat. Caminhos abaixo são relativos à raiz do repositório. Snapshot: **29/10/2026**; conferir os manifestos e os registros mais recentes antes de executar.

## Primeira leitura

1. Ler [AGENTS.md](../AGENTS.md), [briefing original](PROJECT_BRIEF.md), início de [DECISIONS.md](DECISIONS.md) e [PROGRESS.md](PROGRESS.md).
2. Identificar o pedido atual do usuário. O briefing/M0 e notas antigas são históricos; não reiniciar fases já feitas nem interpretar este guia como autorização para tarefas externas.
3. Consultar a [wiki](wiki/Home.md) e carregar somente a skill pertinente. [Backlog](BACKLOG.md) informa prioridades e critérios, não agentes executando em segundo plano.

## Onde o projeto está

| Frente | Referência atual e limites |
| --- | --- |
| Produto Mac | Build privada aceita **0.1.7 / build 8**, Apple Silicon; menu F1/Start, volume, tamanho, fullscreen, mouse livre e captura opcional F2 |
| Execução | Recompilação estática com fallback interpretado medido. REA/Ghidra auxilia a análise; CdiRecomp emite o código |
| Faces / Gamelon | Percursos iniciais observados; campanhas não certificadas |
| Adventure | Percurso conhecido a 1x com transição/inventário; fluxo livre de tela preta ainda sem causa conclusiva, issue #19 |
| Windows | Pacote x64 cross-compilado, execução real pendente (#23); preview antigo não contém o novo menu |
| Outros alvos | Steam Deck/Proton e Linux planejados; não há aceitação nesses sistemas |
| Localização | Piloto opcional de Adventure: slot vazio e cinco rótulos de botões; não há tradução integral |
| Verificação | Última suíte registrada: **151 testes Python**; builds 0.1.7 passaram 11/11 CTests por runtime. Reexecutar o que se aplicar; não herdar o resultado como teste de uma nova mudança |

Controle físico, áudio físico, outro Mac/macOS 13 e fidelidade independente continuam pendentes. Percentual do backlog conta entregas; percentual de instruções nativas pertence a um percurso e pode incluir BIOS. Nenhum dos dois certifica campanha.

## Descobrir o ambiente antes de construir

```sh
git status --short
git log -5 --oneline
python3 scripts/update_backlog.py --check
python3 -m unittest discover -s tests -v
```

Preservar mudanças existentes. Um clone público permite trabalhar em fontes, documentação e fixtures sintéticas; alguns testes exigem o checkout auditado/compilador/SDL e podem ser pulados. Ele **não** contém mídia, C comercial gerado, seeds de jogo, relatórios completos ou catálogo aceito. Não baixar jogos/BIOS nem inventar esses artefatos. A preparação de uma base de pesquisa está no [README](../README.pt-BR.md); essa base não equivale ao candidato otimizado aceito.

No workspace completo, conferir sem regravar:

| Artefato privado | Função |
| --- | --- |
| `data/private/rea-titles/runtime-catalog.json` | Seleção aceita de `faces`, `gamelon`, `adventure`, com path e SHA-256; resolve a build atual, não escolher a pasta mais recente por nome |
| `<runtime>.build.json` | Proveniência das entradas do runtime; `accepted_inputs()` em `scripts/build_windows_runtimes.py` reconfere os arquivos |
| `dist/Zelda CD-i.app/Contents/Resources/runtime-manifest.json` | Identidade de origem e identidade final assinada dos executáveis empacotados |
| `build/rea-tools/toolchain.json` | Caminhos locais do REA/Node/Ghidra/JDK; não copiar caminhos absolutos de outra máquina |
| `data/private/rea-titles/`, `rea-pilot/`, `player-ui/` | Relatórios, replays e evidências históricas; ler apenas os necessários ao problema |

Não editar fontes referenciadas por uma proveniência aceita. Criar staging/candidato novo; comparar contra o anterior. Alterações só no host podem usar `build_player_ui.py`; nova descoberta de código exige o [gate REA](wiki/REA.md). `build_native_runtimes.py` substitui `build/native/source/` e reemite código: não executá-lo por rotina sobre um workspace aceito sem examinar dependências/proveniência.

## Skills do repositório

| Quando usar | Entrada |
| --- | --- |
| Retomar tarefa, alterar fontes ou preparar entrega | [zeldas-cdi-development](../.agents/skills/zeldas-cdi-development/SKILL.md) |
| Investigar módulo, destinos e cobertura pelo REA | [zeldas-cdi-rea](../.agents/skills/zeldas-cdi-rea/SKILL.md) |
| Reproduzir falha, comparar candidatos e conferir pacote | [zeldas-cdi-validation](../.agents/skills/zeldas-cdi-validation/SKILL.md) |

São Markdown portátil, com metadados opcionais de interface. Se o agente não descobrir `.agents/skills/`, pedir leitura explícita do arquivo; não é necessário registrar MCP, instalar plugins ou alterar configuração global para compreender o fluxo. Não copiar credenciais ou caches privados junto com as skills.

## Prompt para entregar à próxima IA

```text
Continue neste repositório. Leia AGENTS.md e docs/AI_HANDOFF.md,
consulte os registros recentes e carregue a skill local pertinente.
Objetivo desta sessão: [descrever a próxima tarefa].
Confira o estado real antes de mudar algo. Preserve mídia, saves e
candidatos aceitos; use staging e evidências privadas. Registre o que
foi testado e o que ficou pendente. Se faltarem artefatos privados,
avance no que for possível sem inventá-los ou baixar jogos/BIOS.
Siga a autorização do pedido/sessão para commit, push e publicação;
esta documentação não concede autorização adicional.
```

Ao encerrar, atualizar o estado necessário em PROGRESS/DECISIONS e informar: mudança, teste executado, artefatos produzidos, limitação e próximo passo concreto. Não transformar intenção em resultado nem afirmar que outra IA terá acesso ao histórico deste chat.
