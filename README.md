# Zelda CD-i Native Recompilation

Pesquisa de ports nativos de **Link: The Faces of Evil**, **Zelda: The Wand of Gamelon** e **Zelda's Adventure**, começando por Faces of Evil no macOS arm64. Windows e Linux são alvos futuros. A proposta é recompilar código 68070 para código nativo, mantendo OS-9 e os modelos de hardware necessários.

**Estado: fase zero, preparação e auditoria. Nenhum Zelda foi executado ou certificado como recompilado neste projeto.**

O briefing original, incluindo as regras do projeto e o mod opcional PT-BR, está preservado em [docs/PROJECT_BRIEF.md](docs/PROJECT_BRIEF.md).

## Resultados iniciais

- macOS arm64 com Clang, CMake, Python e SDL2 disponíveis; não foi necessário instalar dependências.
- `cdirecomp` obtido em checkout local isolado, sem alterações em arquivos versionados. Frontend compilado; **6/6 testes do compilador e 11/11 testes de componentes do runtime passaram**.
- O runtime completo compilou seus objetos, mas a ligação falhou pela ausência das funções da BIOS recompilada. Essa geração não faz parte desta fase.
- O inventário dos três discos retornou exit 0 e encontrou módulos OS-9 com paridade e CRC válidos: **5 em Faces, 5 em Gamelon e 4 em Adventure**. Isso não comprova descoberta completa de código ou funcionamento dos jogos.
- Ferramenta própria passou **20 testes sintéticos** e verificou os 9 arquivos locais. Mídia, hashes, logs e builds permanecem fora do controle de versão.

## Verificação local

Na raiz do projeto, usando Python 3.9 ou posterior:

```sh
python3 scripts/diagnose_environment.py --json data/private/environment.json
python3 -m unittest discover -s tests -v
python3 scripts/verify_local_media.py --json data/private/media-report.json
```

Para trabalhar apenas com os requisitos de Faces:

```sh
python3 scripts/verify_local_media.py --scope faces
```

O verificador calcula SHA-256 e confere presença, tamanhos, CUE/BIN, Disc Label e amostras de setores Mode-2. Não autentica os dumps nem valida EDC/ECC, todos os recursos ou execução da BIOS. Um lock opcional permite detectar mudanças futuras:

```sh
# Cria um baseline novo dos arquivos observados; recusa sobrescrever um existente.
python3 scripts/verify_local_media.py --write-manifest data/private/media-lock.json
python3 scripts/verify_local_media.py --manifest data/private/media-lock.json
```

O lock `data/private/media-lock.json` já foi criado nesta auditoria. Use `--manifest` para comparar com ele. Os arquivos fornecidos bastam para continuar a pesquisa de Faces. Caminhos e limites: [docs/ROM_REQUIREMENTS.md](docs/ROM_REQUIREMENTS.md).

## Organização

```text
docs/                   decisões, evidências resumidas, arquitetura e roadmap
scripts/                ferramentas próprias, sem dependências externas
tests/                  fixtures sintéticas, sem mídia comercial
roms/ e bios/           mídia local fornecida — ignorada
data/private/           hashes, inventários e logs privados — ignorados
build/                  builds e testes locais — ignorados
upstream-cdirecomp/     referência experimental isolada — ignorada
```

O diretório principal ainda não foi inicializado como repositório Git. Nenhum commit ou push foi realizado. As regras de exclusão foram verificadas em um repositório temporário, sem preparar mídia em um índice.

## Estratégia e documentação

A recomendação inicial é usar o upstream como dependência experimental separada para uma prova não comercial de Faces, com commit fixo. Não começar uma implementação completa antes de medir suas capacidades. Um fork autorizado, contribuição upstream e implementação própria têm custos e restrições diferentes, comparados em [UPSTREAM_AUDIT.md](docs/UPSTREAM_AUDIT.md).

Os arquivos de licença do upstream e do núcleo m68k se intitulam PolyForm Noncommercial, mas **diferem do texto oficial**. Isolar a dependência não elimina restrições de licença. Não foi atribuída licença permissiva ao projeto nem assumida autorização comercial. A auditoria liga os textos exatos e registra as diferenças.

| Documento | Conteúdo |
| --- | --- |
| [ENVIRONMENT](docs/ENVIRONMENT.md) | Diagnóstico deste Mac e como reproduzir |
| [UPSTREAM_AUDIT](docs/UPSTREAM_AUDIT.md) | Commit, licença, proveniência, builds e testes |
| [ARCHITECTURE](docs/ARCHITECTURE.md) | Disco Mode-2, módulos OS-9, recompilação e runtime |
| [ROADMAP](docs/ROADMAP.md) | Marcos, primeiro teste de Faces e checklist manual |
| [LOCALIZATION](docs/LOCALIZATION.md) | Plano do mod PT-BR externo, fontes e legendas |
| [DECISIONS](docs/DECISIONS.md) | Escolhas e suas justificativas |
| [PROGRESS](docs/PROGRESS.md) | Resultados executados e pendências |
| [PHASE_ZERO_PLAN](docs/PHASE_ZERO_PLAN.md) | Escopo e critérios desta etapa |

O mod PT-BR será opcional e ativável sem recompilar, com traduções externas separadas dos recursos comerciais. Nesta fase há somente investigação e planejamento; a execução original deve ser validada primeiro.

## Próximo passo

Mapear entradas e relocação de um módulo real de Faces e definir sua comparação de execução antes de emitir C privado. O teste de integração **FOE-BOOT-001**, que exige cold boot, título, início de jogo e evidência de execução nativa, está definido no roadmap.

Instrução pronta para a próxima execução:

> Continue no marco M1 de Faces of Evil: use o inventário privado já produzido para mapear módulos, entradas e relocação; proponha um teste comparável para o primeiro módulo antes de emitir e compilar código localmente. Mantenha todos os derivados em data/private ou build, registre cobertura e limitações, não altere upstream-cdirecomp e não faça commits ou pushes.

Não incluir BIOS, imagens de disco, recursos extraídos ou código gerado comercial em publicações. Não baixar jogos automaticamente. Leia [AGENTS.md](AGENTS.md) antes de continuar o desenvolvimento.
