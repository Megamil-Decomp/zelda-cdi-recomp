# REA — Adventure, Gamelon e integração do launcher

## Escopo autorizado

Usuário pediu continuidade nos outros dois jogos, priorizando Zelda's Adventure, e uso pela interface que seleciona os três títulos. Faces já tem candidato com correções de fetch e IRQ; preservar sua build aceita pelo usuário. Não alterar mídia, saves originais ou checkout upstream. Sem commits/pushes.

## Plano e aceitação

1. Registrar referências, runtimes existentes e hashes privados. Reproduzir Adventure com cópia de bateria, incluindo menu, entrada no save e transições. Distinguir travamento de lógica, crash e limite do harness.
2. Coletar o ledger completo de destinos observados e medir instruções nativas/interpretadas no mesmo procedimento. Usar REA/Ghidra nos módulos e pontos relevantes; não assumir layout de Subr ou tratar pseudocódigo como fonte original.
3. Gerar candidato estático de Adventure com entradas observadas validadas, emissão estrita e patches já comprovados. Comparar runtime anterior/candidato, imagens e respostas aos controles. Se aparecer divergência, investigar antes de promover.
4. Repetir prova de menor escopo em Wand of Gamelon: boot/menu e primeira área quando alcançável. Registrar limites em vez de atribuir compatibilidade por extrapolação.
5. Integrar os runtimes escolhidos no launcher existente por um catálogo explícito de paths/hashes privados; manter os três títulos, idioma/mod opcional, preferências e diretórios de saves. Corrigir identificação de licença incorreta na interface ao empacotar. Entregar `.app` local verificado, sem mídia incluída.

Testes: `python3 -m unittest discover -s tests -v`, CTest pertinente, emissão sem diagnósticos, checksums e assinatura do pacote, prova real dos caminhos principais de execução. Capturas, seeds, hashes, código comercial gerado e relatórios detalhados ficam exclusivamente em diretórios ignorados. Trechos curtos e proporção nativa não certificam campanha completa nem áudio físico.

## Continuação de 2026-10-29

Ampliar Adventure além da primeira transição: observar movimento e interações em sequência, distinguindo colisão/caminho bloqueado, demonstração automática e espera real de I/O. Conferir entrega e consumo dos inputs se a resposta parecer inconsistente, inicialmente apenas por instrumentação privada. Não mudar o protocolo ou fabricar eventos sem causa comprovada. Investigar com REA novas entradas da execução real e comparar eventual candidato adicional com 0.1.5 antes de alterar o launcher. Preservar um retorno à build já entregue.

Se novas seeds do jogo derem pouco ganho, classificar o fallback por região antes de ampliar a descoberta. Rotinas de BIOS exigem identidade original preservada, entradas sustentadas por execução e análise REA, emissão estrita em árvore privada isolada e ensaio pareado em Adventure. Não sobrescrever a BIOS gerada usada por Faces/Gamelon aceitos. Promover somente se o ganho e a fidelidade do cenário forem demonstrados; checkpoints de retorno continuam privados.
