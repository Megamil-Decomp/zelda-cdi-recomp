# Fase zero — plano e critérios

Data: 2026-10-12. Escopo original preservado em [PROJECT_BRIEF.md](PROJECT_BRIEF.md).

## Trabalho autorizado

1. Auditar o ambiente macOS arm64 e os arquivos já fornecidos, sem alterar a mídia.
2. Obter uma cópia local de `mstan/cdirecomp`, fixar o commit analisado e examinar licença, proveniência, arquitetura e testes. Não editar arquivos versionados do upstream.
3. Compilar e executar componentes independentes de BIOS/discos; guardar builds e logs em `build/` e `data/private/`.
4. Criar ferramentas próprias de diagnóstico e de verificação da mídia, com testes sintéticos para entradas inválidas.
5. Documentar estratégias, arquitetura, marcos, requisitos de mídia, decisões e localização PT-BR.

Não executar implementação extensa dos jogos, traduzir recursos, gerar código a partir da BIOS, commitar ou fazer push nesta fase.

## Aceitação da fase zero

- Versões reais de compiladores e dependências registradas; ausências e falhas explícitas.
- Auditoria ligada a um commit exato, com testes de componentes sem mídia executados e resultados registrados.
- Comando local capaz de apontar arquivos faltantes, calcular SHA-256 e verificar a estrutura suportada de BIN/CUE. Hash observado deve ser distinguido de hash confiável de referência.
- ROMs, BIOS, código gerado, dados e builds excluídos pelo `.gitignore`; confirmar regras sem incluir a mídia em um índice.
- Proposta de recompilação estática com cobertura mensurável, carregamento dinâmico de módulos e preservação do comportamento original.
- Primeiro teste de aceitação de Faces of Evil definido antes da implementação.
- Nenhuma alegação de jogo recompilado/rodando baseada apenas em testes sintéticos ou inventário de disco.

## Verificações planejadas

- Testes sintéticos do verificador: CUE inválido, arquivo ausente, caminho fora da pasta, setor malformado e divergência de hash.
- Testes e build nativos disponíveis no upstream, com inventário de executados e não executados.
- Verificação local dos três pares BIN/CUE e das três BIOS existentes, com relatório privado.
- Verificação das regras de exclusão em repositório temporário, sem criar commit ou índice com mídia.
