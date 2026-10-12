# Auditoria do cdirecomp — fase zero

Data: 2026-10-12. Ambiente executado: macOS arm64. Escopo: leitura do upstream, compilação e testes sintéticos, sem usar BIOS ou discos e sem editar arquivos versionados do upstream.

## Resultado

O frontend compila como executável nativo arm64 e passou seus seis testes CTest. Os onze testes de componentes do runtime também compilaram e passaram. O teste adicional de aliases de funções passou. Isso demonstra uma base técnica útil para pesquisa no Mac; não demonstra que uma BIOS, o shell ou qualquer Zelda funciona neste ambiente.

O alvo completo `CdiRuntime` compilou seus objetos, mas falhou no link por três símbolos que pertencem ao dispatch da BIOS gerada. A geração da BIOS foi deliberadamente excluída desta fase. O código do upstream e do frontend compartilhado usa um texto de licença com restrição não comercial, identificado como PolyForm Noncommercial 1.0.0, porém modificado em relação ao texto oficial. Recomenda-se mantê-lo como dependência local isolada de pesquisa por enquanto, sem assumir uma licença permissiva para o projeto inteiro.

## Identidade e preservação

| Item | Valor observado |
| --- | --- |
| Origem | <https://github.com/mstan/cdirecomp> |
| Clone local | `upstream-cdirecomp/` |
| Commit auditado | `f3c8d579efb11d5a33c6bc7c935dfbced773e62e` |
| Data do commit | `2026-10-09T10:56:42-07:00` |
| Mensagem do commit | `Record Windows and Linux Hotel Mario v0.0.2 package validation` |
| Submódulo necessário | <https://github.com/mstan/m68k-recomp-core> |
| Commit do submódulo | `ddfa4e1b090b643a9ee596050e7eb345b8b276a2` |
| SHA-256 do `LICENSE` principal | `03912c9ba1b055f2364b5adf318f4ca8a66c640e991f16e9ff5b2a516d3f24e2` |
| SHA-256 do `LICENSE` do core | `265faba0468f73bd44cbd156e072fe32f77ba6e372df2733b3a7595f440973cb` |

O clone foi obtido porque não existia. Executou-se `git submodule update --init --recursive`: o submódulo não vem preenchido em um clone simples e é exigido pelo CMake atual. A etapa não aparece nas instruções principais de build do README. `git status --porcelain=v1` no clone e no core retornou saída vazia após os testes. Nenhum commit ou push foi realizado. Os builds ficam fora do clone, em `build/upstream-audit/`.

## Documentos e código examinados

Foram lidos `README.md`, `PLAN.md`, `TODO.md`, `PRINCIPLES.md`, `PROVENANCE.md`, `LICENSE`, `THIRD-PARTY-NOTICES.md`, `RUNTIME-README.md`, `CLAUDE.md`, `recompiler/PROVENANCE.txt`, os dois `CMakeLists.txt` principais, a configuração do oracle, os documentos de licença/proveniência e CMake do core, os testes de componentes e o teste sintético Python de aliases. Também foram examinados os contratos de dispatch, binding nativo e fallback em `runner/include/cdi_runtime.h`, `runner/src/runtime.c` e `runner/src/cdi_native.c`.

O código atual separa geração estática de C e runtime de hardware. O frontend compartilhado seleciona um perfil SCC68070, com política própria de OS-9 e retomadas assíncronas. O binding de módulos carregados compara SHA-256 da imagem completa e revoga associações após escritas sobrepostas; entradas descobertas por execução alimentam um registro limitado para promoção posterior. Há interpretação de código ainda descoberto ou não promovido. Essa arquitetura é compatível com a meta de recompilação estática, desde que sua cobertura real seja medida durante a execução futura.

O README e `ISSUES.md` registram resultados parciais de Hotel Mario em outras máquinas e limitações de gameplay, persistência e confiabilidade. São relatos upstream, não testes repetidos nesta auditoria. Não foi encontrada validação dos três Zelda neste commit.

### Divergências documentais relevantes

- `PLAN.md`, `TODO.md` e `CLAUDE.md` ainda descrevem a extração do frontend como trabalho futuro; `.gitmodules` e o CMake já consomem o core separado.
- `CLAUDE.md` afirma que o CRC de módulos ainda não foi verificado; o teste atual `Os9ModuleTest` usa um módulo sintético codificado independentemente e verifica CRC, paridade, truncamento e corrupção.
- `CLAUDE.md` orienta leitura/espelhamento de código do oracle, mas `PRINCIPLES.md` e `PROVENANCE.md` estabelecem especificações e comparação de comportamento como base, excluindo fonte de emulador da implementação. Para este projeto, usar apenas comparação de comportamento e documentação de hardware.
- `TODO.md` conserva um aviso histórico de limpeza do Git, enquanto `PROVENANCE.md` afirma que a história vendorizada foi removida. Esta auditoria não certifica a limpeza de toda a história nem prova independentemente as alegações de autoria/clean room.
- `RUNTIME-README.md` descreve um checkpoint antigo de Windows BIOS-only; não representa sozinho o escopo do commit atual.

Essas diferenças precisam ser esclarecidas antes de reutilizar instruções históricas como requisitos atuais. Os arquivos originais foram preservados.

## Licença e dependências

### Restrição não comercial e texto modificado

Ambos os arquivos `LICENSE` se identificam como PolyForm Noncommercial 1.0.0, copyright Matthew Stan. O texto local permite uso, alterações e distribuição dentro de finalidades permitidas, limita o uso à esfera não comercial e não concede sublicenciamento. Acrescenta uma declaração sobre lucro e um contato comercial. A licença do compilador/runtime não fornece direitos sobre firmware, jogos ou recursos Philips/Nintendo.

Há uma diferença material em relação ao [texto oficial da PolyForm](https://polyformproject.org/licenses/noncommercial/1.0.0): o bloco de copyright foi reescrito e as seções de distribuição, avisos, alterações/obras novas e patente não estão presentes nos arquivos locais. Portanto, registrar a versão e preservar os textos exatos; não substituir silenciosamente pelo texto padrão. Esclarecer com o mantenedor a licença pretendida antes de redistribuição ou uso comercial. Esta é uma identificação técnica dos termos encontrados, não uma determinação jurídica.

A restrição comercial conflita com o critério de liberdade por área de atividade da [Open Source Definition da OSI](https://opensource.org/osd). Assim, chamar o conjunto baseado nesse upstream de software de código aberto sem qualificar essa restrição seria impreciso. Ferramentas originais deste workspace podem ter licença própria a escolher; isso não relicencia código upstream incorporado.

### Componentes encontrados

| Componente | Situação | Licença/proveniência observada |
| --- | --- | --- |
| cdirecomp | Fontes de frontend e runtime | Texto upstream modificado, identificado como PolyForm Noncommercial 1.0.0 |
| m68k-recomp-core | Submódulo obrigatório dos alvos atuais | Mesma restrição e texto modificado; proveniência declarada de `segagenesisrecomp`/cdirecomp |
| `toml.c` / `toml.h` | Parser incorporado ao frontend | MIT, copyright CK Tan, aviso preservado nos arquivos; não citado no `THIRD-PARTY-NOTICES.md` principal |
| SDL2 | Interface de plataforma necessária ao CMake do runner | Aviso zlib-style em `THIRD-PARTY-NOTICES.md` |
| SDL2 local | `sdl2-compat` 2.32.70, arm64 | Aviso zlib-style local em `/opt/homebrew/opt/sdl2-compat/LICENSE.txt` |
| SDL3 local | Dependência runtime 3.4.10 do pacote instalado | Aviso zlib-style local em `/opt/homebrew/opt/sdl3/LICENSE.txt` |
| CeDImu | Oracle opcional, ausente e não baixado | Excluído do player e do recompiler pelas regras atuais; licença/versão não auditadas nesta fase |
| clown68000/clowncommon | Não exigidos pelo CMake auditado | Upstream declara remoção dos caminhos antigos; não se certificou a história completa |

O pacote instalado oferece a API SDL2 através de SDL3, conforme a [documentação oficial do sdl2-compat](https://github.com/libsdl-org/sdl2-compat). O futuro teste visual/sonoro deverá registrar essa escolha, que pode diferir das instalações SDL2 clássicas utilizadas pelo upstream. `otool -L` de `PlayerConfigTest` confirma o vínculo com `/opt/homebrew/opt/sdl2-compat/lib/libSDL2-2.0.0.dylib`. Nenhuma dependência foi instalada ou atualizada.

## Ambiente e comandos reproduzíveis

Ambiente observado: macOS `27.0.1` (`26A434`), Darwin arm64; Apple Clang `21.0.0` (`clang-2100.3.34.2`), target `arm64-apple-darwin27.0.0`; CMake `4.4.4`; Python em `/usr/bin/python3`; Homebrew em `/opt/homebrew/bin/brew`. Ninja e pkg-config não estavam no PATH. Usou-se o gerador Unix Makefiles disponível, sem instalar ferramentas. O CMake encontrou SDL2 usando o prefixo `/opt/homebrew`.

Comandos a partir da raiz do workspace:

```sh
git clone https://github.com/mstan/cdirecomp.git upstream-cdirecomp
git -C upstream-cdirecomp submodule update --init --recursive

cmake -S upstream-cdirecomp/recompiler -B build/upstream-audit/recompiler \
  -G 'Unix Makefiles' -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build build/upstream-audit/recompiler --parallel 4
ctest --test-dir build/upstream-audit/recompiler --output-on-failure

cmake -S upstream-cdirecomp/runner -B build/upstream-audit/runner \
  -G 'Unix Makefiles' -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DCDI_COSIM_BUILD=OFF -DCMAKE_PREFIX_PATH=/opt/homebrew
cmake --build build/upstream-audit/runner --parallel 4 --target \
  SlaveTest CdiNativeTest CdiSha256Test CdiNvramTest PeriphTest \
  Mcd212VideoTest M68kArithTest CdiInputTest CdiAudioTest CdicTest PlayerConfigTest
ctest --test-dir build/upstream-audit/runner --output-on-failure

cmake --build build/upstream-audit/recompiler --parallel 4 \
  --target CdiRecompFrontendFixture
python3 upstream-cdirecomp/tools/test_function_aliases.py \
  --recompiler build/upstream-audit/recompiler/CdiRecompFrontendFixture

# Resultado esperado deste checkpoint sem BIOS gerada: falha no link.
cmake --build build/upstream-audit/runner --parallel 4 --target CdiRuntime
```

O Python de aliases usa fixtures sintéticos e arquivos temporários, sem mídia comercial. Os testes C usam verificações próprias, não `assert()` removido por `NDEBUG`; a configuração Release conserva essas verificações. O build cria um `fixture.bin` sintético privado, não uma ROM comercial.

## Resultados executados

Logs brutos privados ficam em `build/upstream-audit/logs/`. Saídas resumidas abaixo correspondem às execuções desta auditoria.

| Operação | Exit | Resultado/log |
| --- | --- | --- |
| Clone e inicialização do core | 0 / 0 | Clone e checkout do SHA acima |
| Configure recompiler | 0 | `recompiler-configure.log` |
| Build recompiler e fixtures | 0 | `recompiler-build.log`; `CdiRecomp` e `CdiRecompBios` gerados |
| CTest recompiler | 0 | 6/6 passed; `recompiler-ctest.log` |
| Configure runner | 0 | `runner-configure.log`; Threads e SDL2 encontrados |
| Build dos onze componentes | 0 | `runner-components-build.log` |
| CTest runner | 0 | 11/11 passed; `runner-ctest.log` |
| Build frontend fixture | 0 | `frontend-fixture-build.log` |
| Teste Python de aliases | 0 | `function_aliases: all checks passed`; `function-aliases.log` |
| Build de `CdiRuntime` | 2 | Objetos compilados; link falhou; `runner-full-build.log` |

Testes CTest do recompiler executados: `module_seeds`, `module_entries`, `native_pic_execution`, `native_pic_rejects_falloff`, `os9_module_validation`, `disc_filesystem`. Cobrem seeds inválidos, entradas de módulos, emissão e execução relocável sintética, rejeição de falloff, validação de módulos e filesystem sintético.

Testes CTest do runner executados: `ikat_transport`, `native_module_binding`, `sha256`, `cdi_nvram`, `scc68070_peripherals`, `mcd212_video`, `m68k_arithmetic`, `cdi_input`, `cdi_audio`, `cdic`, `player_config`. Cobrem contratos locais de binding/invalidação, hashes, bateria/relógio, periféricos, pixels, aritmética e transporte. Não cobrem a execução integrada de um disco Zelda, renderização por uma janela real ou qualidade de áudio nos dispositivos do Mac.

O build da fixture PIC registrou dois destinos de tabela interior não resolvidos e o teste passou com esse caminho híbrido da fixture. Não é evidência de cobertura nativa completa. O linker avisou sobre redução de alinhamento em dois testes (`__DATA,__common`, `0x8000` para `0x4000`); ambos passaram. Houve também um aviso de comentário `/*` aninhado em `main.c` durante o build completo.

Falha final de link, preservada sem stubs:

```text
Undefined symbols for architecture arm64:
  _call_by_address
  _game_dispatch_has_addr
  _recomp_call_addr
ld: symbol(s) not found for architecture arm64
```

O contrato em `runner/include/cdi_runtime.h` e o uso em `runtime.c` identificam esses símbolos como funções do dispatch gerado. O glob `bios/generated/*.c` não encontrou uma BIOS gerada no clone limpo. Assim, a ausência é consistente com o fluxo de build documentado, e não prova por si só um defeito do compilador arm64. Não se geraram substitutos para fazer o link parecer bem-sucedido.

`file` identificou `CdiRecomp` e `PlayerConfigTest` como `Mach-O 64-bit executable arm64`. Nenhum executável de player foi concluído ou iniciado. Não foram executados smoke tests de BIOS, oracle/co-sim, gameplay, saves ou empacotamento. O inventário posterior da mídia pelo projeto, se realizado, deve ser registrado separadamente; ele não faz parte da validação sem mídia desta auditoria.

## Estratégias

| Estratégia | Benefício | Custo/limite | Avaliação nesta fase |
| --- | --- | --- | --- |
| Fork dentro dos termos aplicáveis | Controle sobre correções, jogo e plataforma | Herda restrições do código incorporado; exige esclarecer licença modificada e manutenção do fork | Viável para pesquisa não comercial; decisão de distribuição pendente |
| Contribuição upstream | Correções de CPU/hardware beneficiam vários títulos | Depende de aceite, fluxo/licença de contribuição e escopo do mantenedor | Preferível para defeitos genéricos comprovados; nenhum envio autorizado ou realizado |
| Dependência local fixada | Mantém evidência, versões e código original separados | Não elimina a licença ao linkar/reutilizar; pequenas adaptações futuras podem exigir estratégia própria | Melhor opção para os próximos experimentos de fase zero/um |
| Implementação própria independente | Permite escolher licença para código autoral e definir contratos próprios | Maior custo de CPU, OS-9, dispositivos e regressão; não pode copiar código restrito e chamá-lo de independente | Reservar para uma exigência permissiva/comercial ou limitações técnicas comprovadas |

Recomendação técnica: manter o checkout local e fixado como ferramenta de pesquisa; desenvolver inventário, verificação de mídia e contratos de projeto de forma separada; validar a BIOS e só depois o primeiro módulo de Faces of Evil em marcos pequenos. Antes de redistribuir uma integração, resolver o texto da licença com o mantenedor e mapear exatamente quais fontes e dependências entram no produto. Uma dependência separada não torna o executável resultante automaticamente permissivo.

## Fontes primárias fixadas

- [README no commit auditado](https://github.com/mstan/cdirecomp/blob/f3c8d579efb11d5a33c6bc7c935dfbced773e62e/README.md).
- [CMake do recompiler](https://github.com/mstan/cdirecomp/blob/f3c8d579efb11d5a33c6bc7c935dfbced773e62e/recompiler/CMakeLists.txt) e [CMake do runner](https://github.com/mstan/cdirecomp/blob/f3c8d579efb11d5a33c6bc7c935dfbced773e62e/runner/CMakeLists.txt).
- [LICENSE exato do cdirecomp](https://github.com/mstan/cdirecomp/blob/f3c8d579efb11d5a33c6bc7c935dfbced773e62e/LICENSE) e [LICENSE exato do core](https://github.com/mstan/m68k-recomp-core/blob/ddfa4e1b090b643a9ee596050e7eb345b8b276a2/LICENSE).
- [Proveniência declarada](https://github.com/mstan/cdirecomp/blob/f3c8d579efb11d5a33c6bc7c935dfbced773e62e/PROVENANCE.md) e [princípios](https://github.com/mstan/cdirecomp/blob/f3c8d579efb11d5a33c6bc7c935dfbced773e62e/PRINCIPLES.md).
- [PolyForm oficial](https://polyformproject.org/licenses/noncommercial/1.0.0), [OSD](https://opensource.org/osd) e [SDL compatibility layer](https://github.com/libsdl-org/sdl2-compat).

Essas fontes explicam os contratos e alegações upstream; os logs locais acima são a evidência dos resultados efetivamente repetidos no Mac.
