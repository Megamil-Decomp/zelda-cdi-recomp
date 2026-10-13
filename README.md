# 🗡️ Zelda CD-i Native Recompilation (`zelda-cdi-recomp`)

[![Platform](https://img.shields.io/badge/platform-macOS%20Apple%20Silicon-blue.svg)](https://apple.com)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-playable%20at%2060%20FPS-brightgreen.svg)](#current-project-status)
[![Languages](https://img.shields.io/badge/i18n-English%20%7C%20Portugu%C3%AAs-purple.svg)](#launcher-interface)

*English* | [*Português do Brasil*](README.pt-BR.md)

Native static recompilation (AOT) and standalone game player for the classic Philips CD-i trilogy:
- **Link: The Faces of Evil** (1993)
- **Zelda: The Wand of Gamelon** (1993)
- **Zelda's Adventure** (1996)

Instead of traditional software emulation, this project recompiles the original Motorola/Philips SCC68070 machine code (CD-RTOS / OS-9) ahead-of-time directly into native **ARM64 (Apple Silicon)** machine code. This eliminates the high emulation overhead, delivers locked **60 FPS** gameplay with smooth audio pacing, and establishes a clean foundation for future **Windows** and **Linux** ports.

---

## 📸 Screenshots

| Main Launcher (GUI) | Controls & Key Mapping Window |
| :---: | :---: |
| ![Launcher GUI](screenshots/gui.png) | ![Controls Window](screenshots/controls.png) |

| Link: The Faces of Evil | Zelda: The Wand of Gamelon | Zelda's Adventure |
| :---: | :---: | :---: |
| ![Faces of Evil](screenshots/faces-of-evil.png) | ![Wand of Gamelon](screenshots/wand-of-gamelon.png) | ![Zelda's Adventure](screenshots/zeldas-adventure.png) |

---

## 🎮 Current Project Status

- **Locked 60 FPS**: Native execution pipeline running at 60 FPS on Apple Silicon with hardware vsync decoupler and dedicated QoS priority.
- **Link: The Faces of Evil**: Full boot, interactive gameplay menus, cinematic audio and stage progression.
- **Zelda: The Wand of Gamelon**: Full boot, interactive gameplay menus, stage selection and in-game exploration.
- **Zelda's Adventure**: Full boot with Gaspra FMV intro, cutscene scroll, overworld exploration, and seamless screen transitions (IKAT Channel-C disc query support).
- **Native macOS Launcher**: Modern Swift/AppKit desktop application with bilingual support (**English** & **Portuguese (Brazil)**), automated SHA-256 media validation, and standalone `.app` / `.dmg` bundling.
- **Stability & Crash Prevention**: Protected against accidental quits on focus switching or mouse capture changes.

---

## ⚠️ Media Requirements (Bring Your Own Media)

> **LEGAL NOTICE:** This repository **DOES NOT** contain, distribute, or host any proprietary BIOS ROMs, game disc images, copyrighted audio, video, or artwork.

To build and run the recompiled games, you must provide your own legally dumped files:

### 1. CD-i System BIOS
- **File**: `cdi490a.rom` (exactly 524,288 bytes / 512 KiB).
- **Compatible models**: Philips CD-i 490, CD-i 910 or compatible mono-board system BIOS.
- **Note**: Both standard big-endian and byte-swapped (`swap16`) ROM dumps are automatically detected, normalized, and cached in your private workspace without altering your original file.

### 2. Game Disc Images
- **Format**: Raw Mode-2 CD-ROM dumps consisting of a `.cue` sheet and its companion `.bin` data track (2352 bytes/sector).
- **Required Titles**:
  - `Link - The Faces of Evil (Europe).cue` / `.bin`
  - `Zelda - The Wand of Gamelon (Europe).cue` / `.bin`
  - `Zelda's Adventure (Europe).cue` / `.bin`
- **Validation**: The launcher automatically computes the SHA-256 hash of your disc image to confirm that the game revision matches the recompiled binary modules.

---

## 🕹️ Controls

The native runtime uses **SDL2**, supporting keyboard, modern USB/Bluetooth controllers, and mouse cursor input:

### ⌨️ Keyboard
| Action | Default Keys |
| :--- | :--- |
| **Movement / Directional** | Arrow Keys (`↑` `↓` `←` `→`) or `W`, `A`, `S`, `D` |
| **Button 1 (Action / Attack / Jump)** | `Space`, `Enter`, or `Z` |
| **Button 2 (Secondary Item / Cancel)** | `Backspace` or `X` |
| **Toggle Fullscreen** | `F11` or `Alt + Enter` |
| **Quit Game** | `Cmd + Q` or `Cmd + ESC` |

### 🎮 Gamepad (Xbox, PlayStation, Switch Pro, generic USB controllers)
| Action | Controller Mapping |
| :--- | :--- |
| **Movement** | D-Pad or Left Analog Stick |
| **Button 1 (Attack / Confirm)** | Button `A` (Xbox) / `✕` (PlayStation) / `B` (Nintendo) |
| **Button 2 (Secondary Item)** | Button `B` (Xbox) / `○` (PlayStation) / `A` (Nintendo) |

### 🖱️ Mouse
- Mouse motion moves the on-screen CD-i cursor.
- **Left click**: Button 1 (Action / Confirm).

---

## 🛠️ How to Build and Run on macOS

### Prerequisites
- macOS 13.0 or later (Apple Silicon arm64 recommended).
- Xcode Command Line Tools:
  ```sh
  xcode-select --install
  ```
- CMake and SDL dependencies:
  ```sh
  brew install cmake sdl2
  ```

### 1. Clone the Repository
```sh
git clone https://github.com/Megamil-Decomp/zelda-cdi-recomp.git
cd zelda-cdi-recomp
```

### 2. Place Your Media Files
Place your dumps in the local folders (these directories are ignored by Git to protect private files):
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

### 3. Rebuild Native Game Runtimes
```sh
python3 scripts/build_native_runtimes.py --jobs 4
```

### 4. Package Standalone macOS App and DMG
```sh
python3 scripts/build_macos_app.py
```
The output will be created in:
- `dist/Zelda CD-i.app`
- `dist/Zelda-CDi-AppleSilicon.dmg`

To launch:
```sh
open "dist/Zelda CD-i.app"
```

---

## 📋 Roadmap & Backlog

- [x] **Stable 60 FPS native execution** on macOS Apple Silicon.
- [x] **IKAT Channel C support** resolving Zelda's Adventure screen transition disk timeouts.
- [x] **Bilingual launcher** (English & Brazilian Portuguese).
- [ ] **Port to Windows & Linux**: Extend CMake configurations and runner backends for Windows x86_64 and Linux.
- [ ] **Brazilian Portuguese Translation (PT-BR)**: External mod architecture with string replacement, localized fonts, and synchronized cinematic subtitles without modifying original audio.
- [ ] **Mouse Aiming Enhancement**: Refine mouse cursor responsiveness and optional crosshair aiming.
- [ ] **Enhanced Static Coverage**: Eliminate residual module rejections to increase the percentage of pure AOT code.

---

## 🤝 Credits & Acknowledgements

- **cdirecomp** ([mstan/cdirecomp](https://github.com/mstan/cdirecomp)): Upstream CD-i reverse-engineering research and m68k recompiler core by Matthew Stan.
- **N64Recomp & Zelda64Recomp** ([Zelda64Recomp](https://github.com/Zelda64Recomp/Zelda64Recomp)): Pioneers and inspiration in the modern static recompilation scene.
- **libSDL**: High-performance multiplatform audio, video, and input backend.
- **Philips & Nintendo**: Original creators and trademark holders of the Philips CD-i platform and *The Legend of Zelda* franchise.

---

## 📄 License

This project is licensed under the **MIT License** for all original launcher code, scripts, patches, and tooling developed in this repository. See [LICENSE](LICENSE) for details and third-party notices.
