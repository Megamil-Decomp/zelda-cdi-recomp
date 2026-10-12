# Aplicativo Mac — plano de entrega e aceitação

Pedido de 2026-10-12: avançar da auditoria para um aplicativo que permita escolher um dos três jogos, fornecer a mídia e executar no Mac. A autorização atual inclui geração local de código a partir dos arquivos fornecidos e integração experimental. Preservar o checkout upstream original e manter derivados em diretórios privados. Não realizar commits/pushes.

## Implementação

1. Criar cópia de trabalho privada do upstream em `build/native/source/`, gerar BIOS e módulos localmente e compilar runtimes arm64 por título.
2. Testar boot/entrada pelo fluxo normal usando limites de execução, screenshots e métricas. Não afirmar compatibilidade completa com base apenas em shell/título.
3. Implementar launcher AppKit com lista dos títulos, seleção de BIOS e BIN/CUE, conferência da revisão, persistência de caminhos e logs por jogo.
4. Empacotar `.app` e `.dmg` locais com dependências SDL, licença/proveniência e assinatura ad hoc. Não incluir mídia original nos pacotes; código recompilado derivado permanece em pacote privado para uso local.
5. Entregar o aplicativo com estado real por jogo: execução demonstrada, experimental ou indisponível, conforme os testes.

## Aceitação do launcher/pacote

- `.app` abre por interface gráfica e lista os três jogos; caminhos são selecionáveis, sem editar código ou abrir Terminal.
- BIOS e revisão do disco são conferidas; erros são claros e execução não é iniciada com configuração incompatível.
- BIN exige CUE parceiro reconhecido, preservando estrutura. Não fazer conversão destrutiva da mídia.
- Bibliotecas não dependem de paths Homebrew em tempo de execução; assinatura e integridade do bundle verificadas.
- Configuração, NVRAM e logs são gravados em Application Support/Logs do usuário, não dentro do app assinado.
- Fechamento/erro do processo filho é tratado sem travar a interface.

## Aceitação da execução

- BIOS e módulos reais compilam e linkam sem stubs.
- Primeiro gate: boot da BIOS chega à interface do player com screenshot e relatório privado.
- Segundo gate por jogo: início normal do disco chega ao título, com código de jogo nativo efetivamente executado e fallback medido.
- Gate de jogo: iniciar primeira cena e responder a controle normal; registrar imagem/áudio/timing, divergências e limites de teste. Uma certificação de campanha completa continua sendo trabalho separado.
- Falhas em qualquer gate ficam explícitas no estado do jogo e na entrega. A UI pronta não substitui funcionamento dos jogos.

## Limites de escopo

Primeiro pacote é Mac Apple Silicon. Windows/Linux e recompilação automática de qualquer revisão são marcos futuros. Esta build privada tem revisões compatíveis fixadas por hash; não é um decompilador universal nem contém o código-fonte original dos jogos. PT-BR continua planejado e adiado até validação da execução original.
