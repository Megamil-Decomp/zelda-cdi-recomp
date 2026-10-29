# Zelda CD-i Native Recompilation

[![macOS](https://img.shields.io/badge/macOS-Apple%20Silicon-blue)](#current-status)
[![Status](https://img.shields.io/badge/status-experimental-orange)](#current-status)
[![License](https://img.shields.io/badge/license-MIT%20for%20original%20code-green)](#license-and-provenance)

English | [Português do Brasil](README.pt-BR.md)

Native recompilation research and a desktop player for **Link: The Faces of Evil**, **Zelda: The Wand of Gamelon** and **Zelda's Adventure** on Philips CD-i.

Original SCC68070 / CD-RTOS / OS-9 code is statically recompiled to native code, with **measured interpreter fallback** for uncovered paths. REA/Ghidra assists analysis; CdiRecomp remains the code emitter. This is an experimental hybrid runtime, with full campaigns and fidelity still under investigation.

## Progress and Kanban board

<!-- BACKLOG:START -->
[Open the Kanban board](https://github.com/users/Megamil-Decomp/projects/1/views/2) · [Backlog and acceptance criteria](docs/BACKLOG.md)

**15 / 31 registered deliveries completed (48%)** · updated 2026-10-29.

Done: **15** · In progress: **5** · Awaiting validation: **3** · Backlog: **8**.

This counts scoped deliveries equally; it is not a percentage of complete campaigns, effort, fidelity or native-code coverage. Scope changes can lower the percentage.

| Area | Done / planned | Deliveries |
| --- | ---: | ---: |
| Foundation and fidelity | 2 / 4 | 50% |
| Recompilation and runtime | 5 / 8 | 62% |
| Game compatibility | 3 / 7 | 43% |
| Interface and controls | 2 / 4 | 50% |
| Platforms and export | 2 / 5 | 40% |
| PT-BR localization | 1 / 3 | 33% |
<!-- BACKLOG:END -->

The board has **Backlog → In progress → Awaiting validation → Done**, with an acceptance criterion, area and priority on each issue. See [technical results](docs/PROGRESS.md) for evidence and limits.

## Current status

Last accepted private Mac build: **0.1.7 (build 8), 2026-10-29**. There is no public download of the complete game package.

| Area | What is implemented or observed | Still pending |
| --- | --- | --- |
| Faces of Evil | Menu and first-area segments, movement/combat and return to the map | Broader routes, campaign, independent fidelity checks |
| Wand of Gamelon | REA-assisted static entries; map and Sakado/shop-area observations | Paired tests and later areas/campaign |
| Zelda's Adventure | Known 1x route with save loading, transition, damage/return and inventory | An unexplained black-screen flow, later areas/campaign |
| macOS arm64 | Bilingual launcher, media validation, per-title saves, player menu, mouse and portable export | Physical controller/audio and another Mac/macOS 13 acceptance |
| Windows x64 | Cross-compiled runtimes, Win32 launcher and complete private exporter | Real Windows execution; older preview ZIP lacks the new player menu |
| Steam Deck / Linux | Port plan and shared input code | Hardware/Proton tests and native Linux packaging |
| PT-BR | Optional Adventure pilot: empty-slot label and five menu button labels | Remaining game texts, fonts/resources and subtitles |

For Adventure, the paired additional route measured **89.19% → 92.20% native instructions, including BIOS**. A later 1x route measured 92.27%. These are interval-specific instruction ratios, not campaign completion or a speed benchmark. [Method, results and limitations](docs/PROGRESS.md).

Validation recorded for 0.1.7: **142 Python tests**, **11/11 CTests per runtime** (three builds), actual Mac interaction with the host menu/mouse, and boot/shutdown checks of all three packaged binaries. Physical audio/gamepad and Windows execution are not covered by these checks.

## Player menu and controls

**F1 / Start** opens options and pauses game execution and host audio. It provides fullscreen, three window sizes, volume, mouse enable/capture and an informational button map. Host preferences persist per title in `frontend.cfg`.

| Action | Keyboard / mouse | SDL gamepad mapping |
| --- | --- | --- |
| Direction | Arrows or WASD | D-pad / left stick with deadzone |
| CD-i button 1 | Space / Enter / Z / left click | A |
| CD-i button 2 | Backspace / X / right click | B |
| Options / resume | F1 (possibly Fn + F1 on Mac) | Start |
| Fullscreen | F11 or Alt + Enter | Available in options |
| Capture / release cursor | F2 | Available in options |
| Back in host menu | Esc | B |
| Exit game | Cmd + Q / Cmd + Esc, or options menu | Available in options |

A/B refer to SDL's controller mapping; printed button labels vary by controller. Direct left-stick support is implemented and tested synthetically; a physical-controller test is pending. The launcher still needs keyboard/mouse input.

Mouse input works in the focused game window **without requiring capture**. Motion moves the CD-i pointer relatively; it does not place it at the computer pointer's absolute position. F2 optionally confines the cursor. Opening the host menu consumes pending mouse clicks and releases capture.

## Export a private test copy

From a prepared workspace with an accepted Mac application and matching local media:

```sh
python3 scripts/export_private_macos.py
```

This creates a new dated export in ignored `dist/exports/`, including matching BIOS/discs, runtime dependencies and the launcher, without personal saves. On another Apple Silicon Mac, extract the ZIP and open the complete `.app`. The destination does not need Python, REA, Homebrew or a compiler. The app has a local signature and is not Apple-notarized. [Mac export details](docs/PRIVATE_EXPORT.md).

Windows construction/export uses the same project:

```sh
python3 scripts/export_private_windows.py
```

Requires a prepared accepted catalog and the cross-compilation toolchain on the source machine. The resulting Windows folder includes its DLLs and local media. **Real Windows testing remains pending.** [Test checklist](docs/WINDOWS_TESTING.md) · [Portability](docs/PORTABILITY.md) · [Steam Deck plan](docs/STEAM_DECK_PLAN.md).

Complete exports stay private and outside Git. No game or BIOS downloads are provided.

## Build a research baseline on macOS

Requires **Apple Silicon / macOS 13+**, Python 3, Git, Xcode Command Line Tools and CMake. This is the development setup; complete private exports do not need these tools.

```sh
xcode-select --install
brew install cmake

git clone https://github.com/Megamil-Decomp/zelda-cdi-recomp.git
cd zelda-cdi-recomp

git clone https://github.com/mstan/cdirecomp.git upstream-cdirecomp
git -C upstream-cdirecomp checkout f3c8d579efb11d5a33c6bc7c935dfbced773e62e
git -C upstream-cdirecomp submodule update --init --recursive
```

Review [upstream licensing and provenance](docs/UPSTREAM_AUDIT.md). The build verifies the audited revisions and applies patches to a private staging copy. A pinned native SDL2 SDK is downloaded from its official release and built privately for macOS 13; no global SDL installation is replaced.

Provide your own compatible dumps in these ignored directories:

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

BIOS size: 524,288 bytes; big-endian and swap16 normalization are checked locally. Discs use supported raw Mode-2 CUE/BIN pairs. A matching revision is required, not just a matching filename. [Media requirements](docs/ROM_REQUIREMENTS.md).

```sh
python3 scripts/build_native_runtimes.py --jobs 4
python3 scripts/build_macos_app.py
open "dist/Zelda CD-i.app"
```

Outputs remain under ignored `build/` and `dist/`. These commands create a **research baseline**. The accepted optimized 0.1.7 build additionally uses locally observed seeds and an explicit private runtime catalog, which are not distributed as game-derived code. Do not assume a fresh baseline has the same static coverage or acceptance as the private candidate. [REA workflow](docs/REA_WORKFLOW.md) · [Player menu build](docs/PLAYER_MENU_PLAN.md).

Run the project's synthetic tool tests with:

```sh
python3 -m unittest discover -s tests -v
```

## Screenshots

Historical development captures; they are not a certification of the latest build or a complete campaign.

| Launcher | Controls |
| --- | --- |
| ![Launcher](screenshots/gui.png) | ![Controls](screenshots/controls.png) |

| Faces of Evil | Wand of Gamelon | Zelda's Adventure |
| --- | --- | --- |
| ![Faces of Evil](screenshots/faces-of-evil.png) | ![Wand of Gamelon](screenshots/wand-of-gamelon.png) | ![Zelda's Adventure](screenshots/zeldas-adventure.png) |

## Documentation

- [Backlog, priorities and acceptance criteria](docs/BACKLOG.md)
- [Technical progress and limitations](docs/PROGRESS.md) · [Decisions](docs/DECISIONS.md)
- [Architecture](docs/ARCHITECTURE.md) · [Original technical milestones](docs/ROADMAP.md)
- [Optional localization](docs/LOCALIZATION.md) · [REA analysis workflow](docs/REA_WORKFLOW.md)

## License and provenance

[MIT](LICENSE) applies to the original host code and tools authored here. **It does not relicense the upstream runtime, recompiler core, patch context or commercial game code.** The audited upstream contains specific noncommercial terms under a PolyForm Noncommercial title; see the [audit](docs/UPSTREAM_AUDIT.md) before reusing or distributing derivatives. SDL uses its own zlib license.

BIOS, disc images, extracted resources, saves and generated commercial code are excluded from Git. Bring your own compatible media; complete builds remain private. This project is not affiliated with Nintendo or Philips.

Thanks to [mstan/cdirecomp](https://github.com/mstan/cdirecomp) and its m68k core, [N64Recomp](https://github.com/N64Recomp/N64Recomp), [Zelda64Recomp](https://github.com/Zelda64Recomp/Zelda64Recomp) and SDL for the research, references and host technology.
