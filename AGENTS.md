# Zelda CD-i Native Recompilation

Leia `docs/PROJECT_BRIEF.md`, `docs/DECISIONS.md` e `docs/PROGRESS.md` antes de continuar.

- Começar por Faces of Evil; macOS arm64 é o primeiro ambiente. Windows/Linux são alvos futuros.
- Priorizar recompilação estática e fidelidade. Interpretação é fallback de pesquisa e deve ter sua participação medida; não apresentá-la como recompilação completa.
- Nunca adicionar ROMs, BIOS, discos, recursos extraídos ou código comercial gerado ao Git. Usar `roms/`, `bios/`, `data/private/` e `build/`, todos ignorados.
- Não baixar jogos/BIOS. Não mover ou modificar a mídia fornecida sem necessidade e autorização.
- `upstream-cdirecomp/` é referência local isolada com termos intitulados PolyForm Noncommercial que diferem do texto oficial. Não editar seu código sem autorização explícita; registrar commit, licença e proveniência antes de qualquer reutilização. Não atribuir licença permissiva ao conjunto por conveniência.
- Antes de mudanças grandes, documentar plano, aceitação e testes. Registrar decisões em `docs/DECISIONS.md` e resultados reais em `docs/PROGRESS.md`.
- Não realizar commits ou pushes sem confirmação do usuário.
- Localização PT-BR será mod externo opcional. Nesta etapa, apenas investigar formatos e arquitetura; preservar textos/áudio originais e manter recursos protegidos fora das traduções autorais.
- Executar `python3 -m unittest discover -s tests -v` para ferramentas próprias. Os testes devem usar dados sintéticos, nunca depender de mídia comercial.
- Usar relatórios em `data/private/` para hashes locais, inventários detalhados, logs e eventuais rastros derivados do jogo.
