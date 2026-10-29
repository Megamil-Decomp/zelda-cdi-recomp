# Protótipo visual opcional dos botões Adventure

Autorização: usuário pediu aplicar e testar os demais rótulos. O codec/recurso original ainda não foi identificado. Para permitir teste funcional, implementar composição no host, depois da cópia do framebuffer, sem modificar RAM, disco, BIOS, saves ou hitboxes. Não apresentar isso como tradução do recurso gráfico original.

Reconhecimento: dimensões exatas e hashes de três regiões estáticas da tela original, em configuração privada externa. Somente PT-BR/Adventure recebe esse arquivo. Falha na identificação ou configuração mantém original. Evitar regiões de cursor, nome do save e realce de seleção. Não aplicar por simples posição/temporizador.

Apresentação: placas de fundo com rótulos autorais JOGAR, CRIAR, APAGAR, COMO JOGAR, SAIR, em fonte bitmap autoral mínima. Aparência provisória, distinta da arte original. Idioma inglês permanece intacto; outros jogos não recebem mod.

Aceitação: reconhecer menu real, rejeitar tela de boot e dados sintéticos divergentes, desenhar dentro das áreas previstas, testar seleção/clique de um botão, gerar captura composta de uma execução real, executar suite sintética e empacotar versão separada. Nenhuma mídia ou hash comercial em Git. Sondas temporárias não entram no pacote.

## Resultado — 2026-10-14

Implementado em `app/native/cdi_menu_mod.h` com integração reproduzível `0006-adventure-menu-overlay.patch`. Composição ocorre somente na cópia de pixels do frontend SDL, após hardware produzir o framebuffer. Fonte mínima 5x7 é autoral; paleta/arte comercial não são incorporadas ao código. Perfil com fingerprints fica privado, empacotado externamente em Resources.

Reconhecimento exige dimensões exatas e ao menos dois de três hashes RGB: uma região da moldura e duas regiões dos botões. Permite um realce/cursor alterar uma região sem assumir tela por temporizador. Perfil inválido, dimensões divergentes ou menos de dois hashes mantêm os pixels originais. Não existe garantia universal para todas as telas ainda não observadas: testar mais estados do menu.

Captura real composta: `data/private/localization/menu-investigation/composed.png`. Placas ampliadas após primeira inspeção para não deixar letras originais nas bordas. Ainda não reproduzem a estética da fonte original; SAIR cobre parte do pergaminho. Texto/posições vêm do perfil externo e áreas de clique não são modificadas.

Clique real em COMO JOGAR publicou pressão/leitura/liberação pelo IKAT e abriu o FMV de instruções. Captura desse FMV em `menu-investigation/final.png`. Teste do mesmo compositor sobre capturas reais: menu reconhecido e modificado; instruções não reconhecidas e pixels intactos (`overlay-acceptance.json`). Demais botões e retorno/campanha ficam para teste interativo do usuário.

Suite: 44 testes Python aprovados (inclui seis fixtures C do compositor). Patch reaplicado em árvore mínima e comparado à staging. Runtime reconstruído sem sonda de captura; upstream original permanece limpo. App/DMG 0.1.4 em `dist/ptbr-menu/`, assinatura profunda verificada pelo empacotador e novamente após build. ROMs/BIOS/saves originais não foram escritos; teste usou cópia privada da NVRAM.

Construção:

```sh
python3 scripts/build_macos_app.py --output dist/ptbr-menu \
  --text-mod data/private/localization/pilot/adventure-ptbr.txt \
  --menu-mod data/private/localization/menu-investigation/adventure-menu-ptbr.txt
```

GUI português fornece os dois perfis apenas ao Adventure; inglês limpa ambos os overrides. Título do launcher mostra a versão para distinguir pacotes. Tradução limitada ao menu de saves: slots vazios e cinco botões. Instruções, outras telas, falas e outros jogos não traduzidos. Codec/recurso gráfico original continua pendente para uma substituição com maior fidelidade.
