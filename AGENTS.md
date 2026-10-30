# Zelda CD-i Native Recompilation

Leia `docs/PROJECT_BRIEF.md`, `docs/DECISIONS.md` e `docs/PROGRESS.md` antes de continuar.

Para retomar sem o chat, ler `docs/AI_HANDOFF.md`; a wiki começa em `docs/wiki/Home.md`. Carregar apenas a skill pertinente em `.agents/skills/`: `zeldas-cdi-development`, `zeldas-cdi-rea` ou `zeldas-cdi-validation`. Se o agente não carregar skills automaticamente, ler o `SKILL.md` explicitamente. Não é necessário instalar plugins ou registrar MCP para seguir a documentação.

- Faces of Evil foi o marco inicial; macOS arm64 continua o primeiro ambiente. Seguir a prioridade do pedido atual e os registros recentes. Windows já tem cross-build experimental, ainda sem execução real aceita; Linux/Deck permanecem futuros. Instruções de fase zero no briefing são históricas, não reiniciar o projeto por elas.
- Priorizar recompilação estática e fidelidade. Interpretação é fallback de pesquisa e deve ter sua participação medida; não apresentá-la como recompilação completa.
- Nunca adicionar ROMs, BIOS, discos, recursos extraídos ou código comercial gerado ao Git. Usar `roms/`, `bios/`, `data/private/` e `build/`, todos ignorados.
- Não baixar jogos/BIOS. Não mover ou modificar a mídia fornecida sem necessidade e autorização.
- `upstream-cdirecomp/` é referência local isolada com termos intitulados PolyForm Noncommercial que diferem do texto oficial. Não editar seu código sem autorização explícita; registrar commit, licença e proveniência antes de qualquer reutilização. Não atribuir licença permissiva ao conjunto por conveniência.
- Antes de mudanças grandes, documentar plano, aceitação e testes. Registrar decisões em `docs/DECISIONS.md` e resultados reais em `docs/PROGRESS.md`.
- Não realizar commits ou pushes sem confirmação do usuário.
- Localização PT-BR é mod externo opcional; já existe piloto limitado de Adventure. Preservar textos/áudio originais, manter recursos protegidos fora das traduções autorais e seguir o escopo autorizado ao ampliar o piloto.
- Executar `python3 -m unittest discover -s tests -v` para ferramentas próprias. Os testes devem usar dados sintéticos, nunca depender de mídia comercial.
- Usar relatórios em `data/private/` para hashes locais, inventários detalhados, logs e eventuais rastros derivados do jogo.
- Wiki e skills não concedem autorização adicional. Usar a autorização aplicável do pedido/sessão para ações externas; não presumir permissões por exemplos de comandos ou decisões históricas.
