# 🗡️ Zelda CD-i Native Recompilation

[![Platform](https://img.shields.io/badge/platform-macOS%20Apple%20Silicon-blue.svg)](https://apple.com)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-experimental%20playable%20menus-orange.svg)](#status)
[![Languages](https://img.shields.io/badge/i18n-English%20%7C%20Portugu%C3%AAs-purple.svg)](#interface)

Port nativo e recompilador estático para os três clássicos do Philips CD-i:
- **Link: The Faces of Evil** (1993)
- **Zelda: The Wand of Gamelon** (1993)
- **Zelda's Adventure** (1996)

O projeto reconstrói o código original da arquitetura Philips/Motorola SCC68070 (CD-RTOS / OS-9) diretamente para código de máquina nativo **ARM64 (Apple Silicon)**, eliminando a sobrecarga de emulação pesada tradicional e viabilizando futuros portes para **Windows** e **Linux**.

---

## 📸 Screenshots

| Launcher Principal (GUI) | Tela de Controles & Mapeamento |
| :---: | :---: |
| ![Launcher GUI](screenshots/gui.png) | ![Controls Window](screenshots/controls.png) |

| Link: The Faces of Evil | Zelda: The Wand of Gamelon | Zelda's Adventure |
| :---: | :---: | :---: |
| ![Faces of Evil](screenshots/faces-of-evil.png) | ![Wand of Gamelon](screenshots/wand-of-gamelon.png) | ![Zelda's Adventure](screenshots/zeldas-adventure.png) |

---

## 🎮 Status Atual do Projeto

Os três jogos já inicializam a partir do cold boot da BIOS oficial, executam a rotina de boot real do CD-i, reconhecem a mídia e carregam com sucesso:
- **Faces of Evil**: Boot completo até o *Game Menu* (Start Game, Load Game, etc.).
- **Wand of Gamelon**: Boot completo até o *Game Menu* (Start Game, Load Game, etc.).
- **Zelda's Adventure**: Boot completo com introdução em FMV do mago Gaspra e pergaminho da história.
- **Launcher Nativo macOS**: Aplicativo gráfico completo em Swift/AppKit com seleção de jogos, validação automática de checksum SHA-256 da BIOS/Discos, empacotamento em `.app` e instalador `.dmg`.
- **Suporte Multilíngue na Interface**: Alternância dinâmica entre **English** (padrão) e **Português (Brasil)** no launcher.

---

## ⚠️ Requisitos de Mídia (Traga suas próprias ROMs)

> **AVISO IMPORTANTE:** Este repositório **NÃO contém**, distribui ou hospeda nenhuma BIOS, ROM, imagem de disco, áudio ou arte protegida por direitos autorais.

Para utilizar o projeto, você deve fornecer seus próprios arquivos legais:
1. **BIOS do CD-i**:
   - `cdi490a.rom` (512 KiB)
   - O launcher aceita tanto a BIOS original quanto com bytes invertidos (swap16), normalizando-a em cache privado sem alterar seu arquivo original.
2. **Imagens de Disco dos Jogos**:
   - Par de arquivos `.cue` e `.bin` (faixa Mode-2 raw de 2352 bytes por setor) para cada título desejado.
   - O launcher verifica a integridade do disco através do SHA-256 e avisa caso a revisão seja incompatível com os módulos recompilados.

---

## 🕹️ Controles Padrão

O runtime utiliza **SDL2 nativo**, suportando teclado, gamepads USB/Bluetooth e mouse:

### ⌨️ Teclado
| Ação | Teclas Padrão |
| :--- | :--- |
| **Movimento / Direcional** | Setas Direcionais (`↑` `↓` `←` `→`) ou `W`, `A`, `S`, `D` |
| **Botão 1 (Ação / Atacar / Pular)** | `Espaço`, `Enter` ou tecla `Z` |
| **Botão 2 (Item secundário / Cancelar)** | `Backspace` ou tecla `X` |
| **Sair para o Launcher** | `ESC` |
| **Alternar Tela Cheia** | `F11` ou `Alt + Enter` |

### 🎮 Gamepad (Xbox, PlayStation, Switch Pro, genéricos)
| Ação | Botão |
| :--- | :--- |
| **Movimento** | D-Pad ou Analógico Esquerdo |
| **Botão 1 (Atacar / Confirmar)** | Botão `A` (Xbox) / `✕` (PlayStation) |
| **Botão 2 (Item secundário)** | Botão `B` (Xbox) / `○` (PlayStation) |

### 🖱️ Mouse
- O movimento do mouse controla o cursor original do CD-i na tela.
- **Clique esquerdo**: Botão 1 (Ação / Confirmar).

---

## 🛠️ Como Compilar e Executar no macOS

### Pré-requisitos
- macOS 13.0+ (Apple Silicon arm64)
- Xcode Command Line Tools (`xcode-select --install`)
- CMake e dependências SDL:
  ```sh
  brew install cmake sdl2
  ```

### 1. Clonar o repositório
```sh
git clone https://github.com/seu-usuario/zeldas-cdi.git
cd zeldas-cdi
```

### 2. Posicionar sua mídia
Coloque seus arquivos nas pastas locais (essas pastas são ignoradas pelo Git e permanecem 100% privadas):
```text
bios/
  cdi490a.rom
roms/
  Link The Faces of Evil/
    Link - The Faces of Evil (Europe).cue
    Link - The Faces of Evil (Europe).bin
  Zelda The Wand of Gamelon/
    Zelda - The Wand of Gamelon (Europe).cue
    Zelda - The Wand of Gamelon (Europe).bin
  Zeldas Adventure/
    Zelda's Adventure (Europe).cue
    Zelda's Adventure (Europe).bin
```

### 3. Compilar os Runtimes Nativos
```sh
python3 scripts/build_native_runtimes.py
```

### 4. Gerar o Aplicativo (`.app` e `.dmg`)
```sh
python3 scripts/build_macos_app.py
```
O pacote final estará disponível em:
- `dist/Zelda CD-i.app`
- `dist/Zelda-CDi-AppleSilicon.dmg`

Para abrir diretamente:
```sh
open "dist/Zelda CD-i.app"
```

---

## 📋 Backlog & Próximos Passos

- [ ] **Melhorar desempenho**: Otimizar a árvore de emissão de código nativo, eliminar rejeições de módulo por escrita em RAM e reduzir o fallback para o interpretador m68k.
- [ ] **Traduzir jogos para português do Brasil**: Desenvolver a arquitetura de mod externo (injeção em tempo de execução via JSON de strings, novas fontes com acentuação gráfica e legendas sincronizadas nas cinematics sem alterar o áudio original).
- [ ] **Aceitar mouse / mira direta**: Aprimorar a responsividade do cursor e mapear ações de mira rápida com o ponteiro do mouse.
- [ ] **Portar para Windows e Linux**: Adaptar os scripts de compilação e empacotamento para targets Windows (x86_64) e Linux, com suporte a CMake multiplataforma.

---

## 🤝 Créditos e Agradecimentos

- **cdirecomp** ([mstan/cdirecomp](https://github.com/mstan/cdirecomp)): Projeto de pesquisa upstream em engenharia reversa do hardware CD-i e núcleo de recompilação m68k por Matthew Stan.
- **N64Recomp & Zelda64Recomp** ([Zelda64Recomp](https://github.com/Zelda64Recomp/Zelda64Recomp)): Referências e inspiração no modelo de recompilação estática moderna.
- **libSDL**: Camada de áudio, vídeo e entrada de alta performance.
- **Philips & Nintendo**: Criadores e detentores dos direitos intelectuais e comerciais originais do hardware Philips CD-i e da franquia The Legend of Zelda.

---

## 📄 Licença

Este projeto é disponibilizado sob a licença **MIT** para todo o código original, launcher e ferramentas desenvolvidas neste repositório. Consulte o arquivo [LICENSE](LICENSE) para detalhes completos e avisos sobre bibliotecas de terceiros.
