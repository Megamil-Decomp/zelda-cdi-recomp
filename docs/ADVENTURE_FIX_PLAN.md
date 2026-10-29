# Zelda's Adventure — erro na primeira transição

Investigação iniciada em 2026-10-13 a partir da reprodução do usuário: após iniciar e caminhar para baixo, o jogo mostra a mensagem de disco sujo. A renderização continua ativa; a mensagem não comprova defeito na imagem do disco.

## Plano

1. Conferir binários, mídia selecionada e logs atuais, sem alterar mídia, preferências ou saves do usuário.
2. Reproduzir pela entrada normal em uma sessão privada, capturando IKAT, CIAP/CDIC, módulos e setores antes/depois da transição.
3. Distinguir erro da imagem, protocolo de drive e regressões de tempo/seleção de buffers. Não presumir que o ACK genérico do patch 0003 resolve comandos desconhecidos.
4. Corrigir somente a cópia privada do runtime; manter patch reproduzível e teste sintético do comportamento causal.
5. Repetir a primeira transição e transições seguintes, conferir regressões pertinentes e atualizar `.app`/`.dmg` se a correção for demonstrada.

## Aceitação

- Registrar o erro antes da mudança e a mesma sequência de entrada depois.
- Atravessar a saída sul sem a mensagem de disco sujo, mantendo a resposta de controle na próxima tela.
- Testar nova leitura/transição e ausência de fallback de sucesso inventado para erro real.
- Executar testes próprios e componentes de hardware afetados.
- Não afirmar correção completa do jogo nem qualidade de áudio a partir de FPS, boot ou introdução.

As alegações anteriores em `PROGRESS.md` sobre transições corrigidas ainda não têm evidência preservada suficiente e serão reavaliadas. Logs e capturas desta investigação ficam em `data/private/probes/`.

## Resultado de 2026-10-13

Causa reproduzida: alternação de buffers ADPCM permanecia presa após o par esvaziar e o driver repor o mesmo buffer. Isso bloqueava a conclusão de áudio e produzia o erro apresentado pelo jogo. Patch 0004 e regressão sintética registram a sequência; código anterior falha e corrigido passa.

Os critérios de transição passaram na execução privada a 4x e no aplicativo empacotado a 1x, com uma cópia do save do usuário. `.app`/`.dmg` atualizados para 0.1.1, sem modificar mídia/save originais. Detalhes, limites e evidências estão no início de `PROGRESS.md`. Campanha completa continua fora da validação desta correção.
