Você é o engenheiro principal de um projeto open source chamado Zelda CD-i Native Recompilation.

OBJETIVO:
Investigar e desenvolver ports nativos dos três jogos Zelda para Philips CD-i (Faces of Evil, Wand of Gamelon e Zelda's Adventure), inicialmente focando em Faces of Evil, com suporte futuro a macOS, Windows e Linux.

CONTEXTO:
Workspace atual contém upstream-cdirecomp, clone de https://github.com/mstan/cdirecomp.
Referências arquiteturais: https://github.com/N64Recomp/N64Recomp e https://github.com/Zelda64Recomp/Zelda64Recomp.
Usar essas referências apenas para estudo, respeitando licenças e regras de contribuição.

REGRAS:
1. Não assumir que o projeto cdirecomp é reutilizável sem examinar sua licença PolyForm Noncommercial.
2. Não incluir ROMs, BIOS, assets comerciais, imagens de discos ou código derivado protegido no Git.
3. Não baixar automaticamente cópias não autorizadas dos jogos.
4. Manter data/ e builds privados fora do controle de versão.
5. Priorizar recompilação estática, não um wrapper de emulador.
6. Permitir interpretação como fallback de pesquisa, mas medir a cobertura recompilada.
7. Preservar a fidelidade do hardware original antes de implementar melhorias.
8. Não inventar resultados de testes. Executar e registrar evidências.
9. Antes de alterações grandes, criar um plano, critérios de aceitação e testes.
10. Registrar decisões em docs/DECISIONS.md e progresso em docs/PROGRESS.md.

FASE ZERO — EXECUTAR AGORA:
A. Inspecionar o ambiente macOS, arquitetura de CPU, compiladores e dependências.
B. Auditar o código, README, PLAN, TODO, PRINCIPLES, PROVENANCE, LICENSE e testes de upstream-cdirecomp.
C. Identificar se o projeto compila no Mac e testar componentes que não exigem BIOS nem discos.
D. Comparar as alternativas: fork autorizado, contribuição upstream, dependência separada ou implementação própria.
E. Estudar especificamente o formato Green Book Mode-2, os módulos OS-9 e o processo de carregamento dinâmico.
F. Preparar estrutura de diretórios, .gitignore, scripts de diagnóstico, README e AGENTS.md.
G. Criar docs/ARCHITECTURE.md, docs/ROADMAP.md e docs/ROM_REQUIREMENTS.md.
H. Preparar um comando de verificação local que valide presença, hashes e formatos dos arquivos sem publicá-los.
I. Identificar exatamente quais arquivos o usuário precisará fornecer e em quais caminhos.
J. Definir o primeiro teste de aceitação para Faces of Evil.

NÃO iniciar implementação extensa do jogo nesta primeira execução.
NÃO alterar upstream-cdirecomp sem autorização.
NÃO realizar commits ou pushes sem minha confirmação.

ENTREGA:
1. Diagnóstico do ambiente.
2. Comparação das estratégias com justificativas.
3. Arquitetura proposta.
4. Roadmap dividido em marcos pequenos e testáveis.
5. Checklist do que preciso fazer manualmente.
6. Próxima instrução exata para continuar com o Codex.

Comece pela auditoria e execute os testes que forem possíveis sem ROM ou BIOS.

REQUISITO ADICIONAL — LOCALIZAÇÃO PT-BR

O projeto também deverá suportar um mod opcional de tradução para português brasileiro.

1. Preservar todos os textos originais e o comportamento do jogo.
2. Projetar uma camada de localização desacoplada da lógica recompilada.
3. Investigar onde ficam armazenados textos, fontes, imagens contendo palavras e falas das cinematics.
4. Suportar arquivos externos de tradução, preferencialmente JSON ou outro formato simples.
5. Permitir ativar e desativar o mod PT-BR sem recompilar o jogo.
6. Implementar suporte a caracteres acentuados, fontes e quebras de linha.
7. Prever legendas sincronizadas para cinematics, mantendo o áudio original.
8. Não presumir que textos e cinematics sejam recursos facilmente extraíveis: documentar os formatos encontrados e as limitações.
9. Separar arquivos de tradução autorais de recursos protegidos extraídos do disco.
10. Criar documentação para futuras traduções e mods.

Nesta fase, apenas investigar e planejar a arquitetura de localização. Não implementar a tradução antes de validar a execução do jogo.