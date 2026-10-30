# Wiki do projeto

Wiki curta e versionada junto ao código, sem depender de uma wiki remota separada. Começar pelo [handoff para outra IA](../AI_HANDOFF.md).

| Preciso de… | Ler |
| --- | --- |
| Estado atual, diferenças entre Git público e workspace completo | [Continuidade](../AI_HANDOFF.md) |
| Padrão de mudança, testes, entrega e uso de IA | [Desenvolvimento](Development.md) |
| REA: ambiente, entradas, evidências e seeds | [Uso do REA](REA.md) |
| Diagnóstico, TCP, saves e aceitação de candidatos | [Validação](Validation.md) |
| Motivos técnicos e resultados históricos | [Decisões](../DECISIONS.md) · [Progresso](../PROGRESS.md) |
| O que fazer em seguida e como contar entregas | [Backlog](../BACKLOG.md) |
| Arquitetura e origem das dependências | [Arquitetura](../ARCHITECTURE.md) · [Auditoria upstream](../UPSTREAM_AUDIT.md) |
| Construção, exportação e plataformas | [README](../../README.pt-BR.md) · [Mac](../PRIVATE_EXPORT.md) · [Windows](../WINDOWS_TESTING.md) · [Deck](../STEAM_DECK_PLAN.md) |
| Mod PT-BR e limites | [Localização](../LOCALIZATION.md) · [Piloto](../TEXT_PILOT_PLAN.md) · [Compositor](../MENU_OVERLAY_PLAN.md) |

## Mapa mínimo do código

| Caminho | Responsabilidade |
| --- | --- |
| `app/macos/Launcher.swift`, `app/windows/Launcher.c` | Seleção de título, idioma, validação de mídia, processos e dados do usuário |
| `app/native/cdi_player_ui*.h` | Menu, preferências, fonte autoral, ganho PCM e integração SDL |
| `app/native/cdi_text_mod.h`, `cdi_menu_mod.h` | Piloto externo opcional de Adventure |
| `scripts/patches/` | Adaptações reproduzíveis do runtime/core, aplicadas em staging; [índice](../../scripts/patches/README.md) |
| `scripts/prepare_rea_module.py`, `analyze_rea_module.py`, `run_rea.py` | Preparação/validação, análise limitada e CLI REA isolada |
| `scripts/probe_native_runtime.py` | Observação TCP, contadores, input e captura de evidência privada |
| `scripts/build_*.py`, `export_private_*.py` | Construção e empacotamento; não equivalem a aceitação de gameplay |
| `tests/` | Fixtures autorais sintéticas; não adicionar dependência de mídia comercial |

Fontes de verdade: pedido atual e AGENTS para escopo/regras; manifestos conferidos para identidades locais; PROGRESS para resultados; issues/JSON para backlog. Propostas antigas e nomes de pastas não substituem esses registros. Atualizar esta navegação só quando surgir uma rota nova; evitar copiar o histórico técnico para cada skill.
