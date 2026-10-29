# Menu durante o jogo e mouse do computador

## Escopo e aceitação

Atender a prioridade do usuário: F1/Start abre menu de opções, com continuar, tela cheia, tamanho da janela, volume, mouse, captura e mapa informativo dos controles. Implementação autoral no compositor SDL do host, comum aos três títulos; textos em português/inglês de acordo com a interface. Nenhum recurso comercial, memória guest ou fonte extraída será alterado.

Separar entrega de movimento/cliques do mouse e confinamento do cursor: mouse ativo com foco dentro da janela por padrão, captura relativa opcional. Menu libera a captura e bloqueia os inputs para o guest; fechar o menu exige soltar os botões consumidos. Perda de foco limpa estado. Acrescentar analógico esquerdo com deadzone para direções e navegação por controle.

O frontend retorna um estado de pausa ao loop principal, que continua processando janela/sinais sem executar CPU/dispositivos. Pausar áudio do host enquanto o menu estiver aberto. Sair continua pelo caminho de persistência normal. Volume afeta somente PCM copiado para saída SDL. Preferências ficam em arquivo de host separado do player.cfg/NVRAM; não modificar saves pessoais nos ensaios.

Aplicar patch reproduzível em cópias privadas dos candidatos aceitos, mantendo as BIOS/seeds já validadas. Não regenerar jogos por conveniência nem editar o checkout upstream. Validar fixtures sintéticas de menu, ganho, deadzone, pausa/inputs/foco e preferências, suite Python completa, CTest e interação real no Mac com bateria copiada. Conferir que contadores guest param durante o menu e retomam sem catch-up, que o cursor CD-i responde ao mouse e que a saída normal preserva a bateria de teste. Testar pacote final e guardar a versão anterior.

Tradução dos jogos continua como mod externo parcial; este marco traduz os novos textos da interface, mantém o piloto existente e registra próximos recursos sem prometer localização completa. Windows recebe fontes/integração comuns, mas não será declarado testado sem execução nesse sistema.

## Repetir a construção

`python3 scripts/build_player_ui.py` confere a proveniência dos candidatos do catálogo privado aceito, cria variantes isoladas e produz `data/private/player-ui/runtime-catalog-all.json`. `--catalog` escolhe outra referência explícita; fontes, patch, headers e SDL participam da identidade da variante. A ferramenta prepara o SDL2 privado se necessário e não reemite o C dos jogos.

Empacotar o catálogo com `scripts/build_macos_app.py --runtime-catalog data/private/player-ui/runtime-catalog-all.json`, passando os perfis opcionais de tradução já aceitos e um destino privado de teste. Após validar/promover o app, `python3 scripts/export_private_macos.py` continua gerando uma cópia completa nova para outro Mac. Resultados reais e caminhos de evidência estão em `PROGRESS.md`.
