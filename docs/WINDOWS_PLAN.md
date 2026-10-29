# Windows x64: primeiro pacote privado de teste

## Escopo e aceitação

Manter o mesmo projeto e reutilizar o C gerado e os patches dos candidatos aceitos. Cross-compilar os três runtimes e uma interface Win32 a partir do Mac. Preparar ZIP x64 com SDL2, mídia local validada, perfis PT-BR opcionais e saves/logs separados por título. Não modificar upstream, mídia original ou pacote macOS. Não incluir saves pessoais. Código comercial gerado e ferramentas/dependências ficam ignorados; nenhum upload.

1. Instalar/verificar compilador MinGW e obter SDL2 Windows na fonte oficial, registrando identidade privada.
2. Conferir proveniência e hashes dos candidatos macOS; copiar suas fontes para staging Windows isolado, preservando as BIOS diferentes de Adventure e Faces/Gamelon.
3. Compilar uma prova Faces, depois os três runtimes; resolver apenas falhas de portabilidade demonstradas. Conferir formato PE x64 e dependências. Não substituir código comercial por stubs.
4. Criar launcher Win32 com seleção dos três títulos, hashes de mídia/runtime, normalização da BIOS em cache, persistência local, logs e escolha do mod parcial. O computador destino não deve precisar de Python, compilador ou REA.
5. Automatizar build incremental e exportação por Python, destinos privados datados e validação do ZIP. Executar testes sintéticos locais e testes Windows quando houver ambiente capaz de executá-los. Sem Windows disponível, declarar explicitamente cross-compilação e inspeção estática, sem alegar gameplay validado no Windows.

O primeiro alvo é Windows x64. Windows ARM64 e consoles continuam separados. Critérios: build completa sem símbolos ausentes, mídia/hash consistentes, DLLs não sistêmicas empacotadas e instruções de teste simples. Relatórios e hashes em `data/private/windows/`, builds em `build/windows/`, pacote em `dist/`.
