# Roadmap

O acompanhamento atual fica no [quadro e backlog](BACKLOG.md), com entregas, prioridades, estados e critérios de aceitação. Os marcos abaixo preservam os critérios técnicos originais; não indicam, isoladamente, que cada condição já foi atendida. Evidências e limitações atuais estão em [PROGRESS.md](PROGRESS.md).

Cada marco termina com resultados reproduzíveis e uma lista de limitações. Não tratar um inventário ou uma janela aberta como jogo recompilado.

| Marco | Trabalho | Critério de saída |
| --- | --- | --- |
| M0 — preparação | Auditoria, ferramentas locais, requisitos e arquitetura | Testes sem mídia e verificação local registrados; licença e limites explícitos |
| M1 — primeiro código de Faces | Inventário detalhado de módulos/entradas, investigação de relocação e código carregado em RAM; emissão privada de um módulo validado | Módulo identificado por SHA-256, entradas justificadas, C gerado compilando em arm64 e fixture de execução comparada ao comportamento 68070 de referência; registrar instruções sem suporte |
| M2 — BIOS e boot | Integração isolada, BIOS gerada localmente, dispositivos e OS-9 reais | Cold boot chega ao player; disco de Faces alcança título/início de jogo com log de dispatch nativo, sem alteração do upstream sem autorização |
| M3 — primeira cena jogável | Entrada, imagem, áudio e temporização | Iniciar jogo, movimentar e agir na primeira cena com entrada normal; repetir cold boot e medir cobertura e desempenho |
| M4 — percurso e persistência | Mapas, transições, mortes, cinematics, save/restore | Percursos e restauração corretos com evidência, sem saltos artificiais de estado; enumerar caminhos não testados |
| M5 — localização e ports | Hooks de mod externos; Windows/Linux; PT-BR inicial | Jogo original já validado; mod liga/desliga sem recompilar; acentos e legendas testados; builds por plataforma |
| M6 — outros títulos | Wand of Gamelon e Zelda's Adventure, cada qual com seu inventário | Repetir M1–M4 por título; não presumir compatibilidade por compartilharem a plataforma |

## Primeiro teste de aceitação de Faces of Evil

**FOE-BOOT-001** é o primeiro teste de integração do jogo. Preparar seus critérios agora, executar somente quando o runtime e os módulos estiverem integrados:

1. Usar BIOS e disco identificados no lock local, build Release arm64, configurações padrão e NVRAM privada nova. Guardar identidade do build e mídia no relatório privado.
2. Fazer cold boot, entrar pelo fluxo normal do player e iniciar o disco. Não injetar PC, não pular carregamento nem substituir funções do jogo por stubs para atingir o título.
3. Alcançar a tela de título e iniciar a primeira cena jogável com entrada normal. Confirmar resposta de movimento/ação; comparar imagem, áudio e duração dos eventos com uma referência identificada.
4. Registrar módulos carregados, base/endereço, identidade do código, blocos nativos executados, instruções interpretadas e motivo de fallback. Se a lógica do jogo executou só no intérprete, o teste de recompilação não passa.
5. Repetir três cold boots isolados. Falhas, timeout e dispositivos não implementados contam como falha ou limitação explícita, nunca como sucesso implícito.

O prazo máximo de boot deve ser definido e registrado após obter uma referência temporizada. Não inventar uma duração agora. Para M3, exigir participação nativa mensurável na lógica do jogo; o alvo de produto permanece eliminar fallback nos caminhos aceitos, com erros explícitos para código não coberto.

## Próximas frentes

Consultar as issues do [backlog atual](BACKLOG.md): investigar o fluxo de tela preta de Adventure, ampliar percursos/cobertura estática e validar Windows, controles e áudio físicos. Steam Deck/Linux e tradução mais ampla têm aceitação separada. Prioridades podem mudar conforme novas falhas reproduzíveis; não usar a sequência histórica M0–M6 como lista de execução obrigatória.

## Pendências manuais

- Não é preciso fornecer mais mídia para continuar a pesquisa de Faces.
- Antes de distribuir código baseado no upstream, definir se o escopo será não comercial ou obter termos apropriados; uma dependência separada não elimina a restrição.
- O código próprio foi publicado sob MIT; revisar proveniência e resolver termos específicos antes de distribuir derivados do runtime upstream. MIT não relicencia o conjunto.
- Uma referência de execução em hardware ou comparador independente será necessária para certificar fidelidade; os testes atuais não a substituem.
