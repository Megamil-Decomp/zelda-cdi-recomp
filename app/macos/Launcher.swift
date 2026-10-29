import AppKit
import CryptoKit
import Foundation

// MARK: - Internationalization (i18n)

private enum AppLanguage: String, CaseIterable {
    case english = "en"
    case portuguese = "pt-BR"

    var displayName: String {
        switch self {
        case .english: return "English"
        case .portuguese: return "Português (Brasil)"
        }
    }

    var flagTitle: String {
        switch self {
        case .english: return "🇺🇸 English / Original"
        case .portuguese: return "🇧🇷 Português (Brasil) — parcial"
        }
    }
}

private struct L10n {
    static var currentLanguage: AppLanguage {
        get {
            if let saved = UserDefaults.standard.string(forKey: "appLanguage"),
               let lang = AppLanguage(rawValue: saved) {
                return lang
            }
            return .english // English default as requested
        }
        set {
            UserDefaults.standard.set(newValue.rawValue, forKey: "appLanguage")
        }
    }

    static func t(_ key: String) -> String {
        let isPt = currentLanguage == .portuguese
        switch key {
        // App header
        case "app.subtitle":
            return isPt ? "Biblioteca local · macOS arm64 · versão experimental" :
                          "Local library · macOS arm64 · Experimental port"
        case "app.library_title":
            return isPt ? "SEUS JOGOS" : "YOUR GAMES"
        case "app.note":
            return isPt ? "PT-BR parcial: slots vazios e botões do menu de Adventure. Reinicie o jogo para aplicar o idioma." :
                          "Partial PT-BR: empty slots and Adventure menu buttons. Restart the game to apply the language."

        // Media fields
        case "media.bios_title":
            return isPt ? "BIOS CD-i" : "CD-i BIOS"
        case "media.disc_title":
            return isPt ? "Disco do jogo" : "Game Disc"
        case "media.bios_hint":
            return isPt ? "Arquivo esperado: cdi490a.rom (tamanho exato: 512 KB)" :
                          "Expected file: cdi490a.rom (exact size: 512 KB)"
        case "media.disc_hint":
            return isPt ? "Arquivo esperado: descritor .cue acompanhado do arquivo .bin" :
                          "Expected file: .cue descriptor accompanied by companion .bin"
        case "media.choose_button":
            return isPt ? "Escolher…" : "Choose…"
        case "media.no_bios":
            return isPt ? "Nenhuma BIOS configurada (esperado: cdi490a.rom)" :
                          "No BIOS configured (expected: cdi490a.rom)"
        case "media.no_disc":
            return isPt ? "Nenhum disco configurado (esperado: arquivo .cue)" :
                          "No disc configured (expected: .cue descriptor file)"
        case "media.panel_bios_msg":
            return isPt ? "Selecione o arquivo da BIOS do CD-i (cdi490a.rom, 512 KB):" :
                          "Select the CD-i BIOS ROM file (cdi490a.rom, 512 KB):"
        case "media.panel_disc_msg":
            return isPt ? "Selecione o descritor .cue correspondente ao disco do jogo:" :
                          "Select the companion .cue descriptor for the game disc:"
        case "media.panel_select":
            return isPt ? "Selecionar" : "Select"

        // Buttons
        case "btn.start":
            return isPt ? "Iniciar jogo" : "Start Game"
        case "btn.stop":
            return isPt ? "Parar" : "Stop"
        case "btn.controls":
            return isPt ? "Controles…" : "Controls…"
        case "btn.open_log":
            return isPt ? "Abrir log" : "Open Log"
        case "btn.close":
            return isPt ? "Concluir" : "Done"

        // Status
        case "status.ready":
            return isPt ? "Escolha um jogo e informe sua mídia." : "Choose a game and provide your media."
        case "status.selected":
            return isPt ? "selecionado. Os arquivos serão verificados ao iniciar." : "selected. Files will be validated upon launch."
        case "status.verifying_bios":
            return isPt ? "Verificando BIOS…" : "Verifying BIOS…"
        case "status.verifying_disc":
            return isPt ? "Verificando disco de" : "Verifying disc for"
        case "status.failed_verification":
            return isPt ? "A mídia não passou na verificação." : "Media verification failed."
        case "status.running":
            return isPt ? "em execução. Use a janela do jogo; o log registra a sessão." : "is running. Use the game window; logs record this session."
        case "status.stopping":
            return isPt ? "Encerrando o runtime…" : "Stopping runtime…"
        case "status.exited_clean":
            return isPt ? "encerrado. Consulte o log para detalhes da sessão." : "exited normally. See log for details."
        case "status.exited_error":
            return isPt ? "encerrou com erro. Abra o log para investigar." : "exited with an error. Open log to inspect."
        case "status.testing":
            return isPt ? "Em teste" : "In testing"
        case "status.unavailable":
            return isPt ? "Ainda indisponível" : "Unavailable"
        case "status.compatibility_note":
            return isPt ? "Compatibilidade em validação; a presença na lista não comprova que o jogo esteja jogável." :
                          "Compatibility in testing; title presence does not guarantee full gameplay."

        // Menus
        case "menu.about":
            return isPt ? "Sobre Zelda CD-i" : "About Zelda CD-i"
        case "menu.hide":
            return isPt ? "Ocultar Zelda CD-i" : "Hide Zelda CD-i"
        case "menu.quit":
            return isPt ? "Sair do Zelda CD-i" : "Quit Zelda CD-i"
        case "menu.file":
            return isPt ? "Arquivo" : "File"
        case "menu.choose_disc":
            return isPt ? "Escolher disco…" : "Choose Disc…"
        case "menu.open_log":
            return isPt ? "Abrir último log" : "Open Latest Log"
        case "menu.open_data":
            return isPt ? "Abrir pasta de dados" : "Open Data Folder"
        case "menu.language":
            return isPt ? "Idioma" : "Language"
        case "menu.help":
            return isPt ? "Ajuda" : "Help"
        case "menu.controls":
            return isPt ? "Controles do Jogo…" : "Game Controls…"

        // Controls Sheet
        case "controls.title":
            return isPt ? "Controles do Jogo" : "Game Controls"
        case "controls.subtitle":
            return isPt ? "Mapeamento padrão suportado pelo runtime SDL2 nativo" :
                          "Default mappings supported by native SDL2 runtime"
        case "controls.keyboard":
            return isPt ? "Teclado" : "Keyboard"
        case "controls.movement":
            return isPt ? "Movimentação:" : "Movement:"
        case "controls.movement_desc":
            return isPt ? "Setas direcionais ou W, A, S, D" : "Arrow Keys or W, A, S, D"
        case "controls.btn1":
            return isPt ? "Botão 1 (Ação / Atacar / Pular):" : "Button 1 (Action / Attack / Jump):"
        case "controls.btn1_desc":
            return isPt ? "Espaço, Enter ou tecla Z" : "Space, Enter, or Z key"
        case "controls.btn2":
            return isPt ? "Botão 2 (Item secundário / Menu):" : "Button 2 (Subweapon / Menu):"
        case "controls.btn2_desc":
            return isPt ? "Backspace ou tecla X" : "Backspace or X key"
        case "controls.exit":
            return isPt ? "Sair para o Launcher:" : "Exit to Launcher:"
        case "controls.exit_desc":
            return isPt ? "Tecla ESC" : "ESC key"
        case "controls.fullscreen":
            return isPt ? "Alternar Tela Cheia:" : "Toggle Fullscreen:"
        case "controls.fullscreen_desc":
            return isPt ? "F11 ou Alt + Enter" : "F11 or Alt + Enter"

        case "controls.gamepad":
            return isPt ? "Controle (Gamepad / Joystick)" : "Gamepad (Controller)"
        case "controls.gamepad_dpad":
            return isPt ? "D-Pad ou Analógico Esquerdo:" : "D-Pad or Left Analog Stick:"
        case "controls.gamepad_dpad_desc":
            return isPt ? "Movimentação do personagem / cursor" : "Character movement / cursor"
        case "controls.gamepad_a":
            return isPt ? "Botão A (Xbox) / ✕ (PlayStation):" : "A Button (Xbox) / ✕ (PlayStation):"
        case "controls.gamepad_a_desc":
            return isPt ? "Botão 1 (Ação / Atacar / Confirmar)" : "Button 1 (Action / Attack / Confirm)"
        case "controls.gamepad_b":
            return isPt ? "Botão B (Xbox) / ○ (PlayStation):" : "B Button (Xbox) / ○ (PlayStation):"
        case "controls.gamepad_b_desc":
            return isPt ? "Botão 2 (Item secundário / Cancelar)" : "Button 2 (Subweapon / Cancel)"

        case "controls.mouse":
            return isPt ? "Mouse / Dispositivo Apontador" : "Mouse / Pointing Device"
        case "controls.mouse_desc":
            return isPt ? "Movimento do mouse move o cursor original do CD-i. Clique esquerdo aciona o Botão 1." :
                          "Mouse movement drives original CD-i pointer. Left-click triggers Button 1."

        case "controls.pref_label":
            return isPt ? "Esquema preferido de teclado:" : "Preferred keyboard scheme:"
        case "controls.pref_opt1":
            return isPt ? "WASD + Espaço / X (Estilo Ação)" : "WASD + Space / X (Action style)"
        case "controls.pref_opt2":
            return isPt ? "Setas + Z / X (Estilo Retro)" : "Arrow Keys + Z / X (Retro style)"

        // Errors & Dialogs
        case "dialog.about_title":
            return isPt ? "Zelda CD-i · versão experimental" : "Zelda CD-i · Experimental Port"
        case "dialog.about_text":
            return isPt ? "Port nativo experimental para Mac Apple Silicon.\n\nForneça seus próprios arquivos de BIOS e imagens CUE/BIN originais. Textos e áudio originais são preservados.\n\nOs componentes têm licenças próprias, incluídas no aplicativo. O runtime contém termos não comerciais." :
                          "Experimental native port for Apple Silicon Mac.\n\nProvide your original BIOS and CUE/BIN disc images. Original game audio and texts are preserved.\n\nComponents have their own licenses, included in the app. The runtime includes noncommercial terms."
        case "dialog.quit_title":
            return isPt ? "Encerrar o jogo e sair?" : "Quit and stop game?"
        case "dialog.quit_text":
            return isPt ? "O jogo ainda está em execução. Ao sair, a sessão será encerrada." :
                          "The game is currently running. Quitting will terminate the active session."
        case "dialog.quit_confirm":
            return isPt ? "Encerrar e sair" : "Quit and Exit"
        case "dialog.quit_cancel":
            return isPt ? "Continuar jogando" : "Keep Playing"

        default:
            return key
        }
    }
}

// MARK: - Data Models

private struct RuntimeManifest: Decodable {
    let schemaVersion: Int
    let bios: BIOSManifest
    let games: [GameManifest]
    let localMediaRoot: String?

    enum CodingKeys: String, CodingKey {
        case schemaVersion = "schema_version", bios, games
        case localMediaRoot = "local_media_root"
    }
}

private struct BIOSManifest: Decodable {
    let size: Int64
    let sha256: String
    let runtimeSHA256: String?
    let byteOrder: String?
    let localRelative: String?

    enum CodingKeys: String, CodingKey {
        case size, sha256
        case runtimeSHA256 = "runtime_sha256"
        case byteOrder = "byte_order"
        case localRelative = "local_relative"
    }
}

private struct GameManifest: Decodable {
    let id: String
    let title: String
    let runtime: String
    let discSHA256: String
    let status: String
    let statusText: String
    let localCueRelative: String?

    enum CodingKeys: String, CodingKey {
        case id, title, runtime, status
        case discSHA256 = "disc_sha256", statusText = "status_text"
        case localCueRelative = "local_cue_relative"
    }
}

private struct SelectedDisc {
    let cue: URL
    let bin: URL
}

private enum LauncherError: LocalizedError {
    case message(String)
    var errorDescription: String? {
        switch self { case .message(let message): return message }
    }
}

// MARK: - Media Validator

private final class MediaValidator {
    private static let fileManager = FileManager.default

    static func regularFile(_ url: URL) throws -> Int64 {
        guard url.isFileURL else {
            throw LauncherError.message(L10n.currentLanguage == .portuguese ? "Escolha um arquivo local." : "Select a local file.")
        }
        let values = try url.resourceValues(forKeys: [.isRegularFileKey, .fileSizeKey])
        guard values.isRegularFile == true, fileManager.isReadableFile(atPath: url.path) else {
            let msg = L10n.currentLanguage == .portuguese ?
                "O arquivo não pode ser lido: \(url.lastPathComponent). Se ele foi movido, escolha novamente." :
                "Cannot read file: \(url.lastPathComponent). If it was moved, select it again."
            throw LauncherError.message(msg)
        }
        return Int64(values.fileSize ?? 0)
    }

    static func disc(at selectedURL: URL) throws -> SelectedDisc {
        var cue = selectedURL.standardizedFileURL
        if cue.pathExtension.lowercased() == "bin" {
            let directory = cue.deletingLastPathComponent()
            let stem = cue.deletingPathExtension().lastPathComponent
            let siblings = try fileManager.contentsOfDirectory(at: directory,
                includingPropertiesForKeys: nil, options: [.skipsHiddenFiles])
            guard let companion = siblings.first(where: {
                $0.pathExtension.lowercased() == "cue" &&
                $0.deletingPathExtension().lastPathComponent.caseInsensitiveCompare(stem) == .orderedSame
            }) else {
                let msg = L10n.currentLanguage == .portuguese ?
                    "Este BIN precisa do arquivo CUE com o mesmo nome na mesma pasta. Escolha o CUE original do disco." :
                    "This BIN requires a companion CUE file with the same name in the same folder. Select the original CUE."
                throw LauncherError.message(msg)
            }
            cue = companion
        }
        guard cue.pathExtension.lowercased() == "cue" else {
            let msg = L10n.currentLanguage == .portuguese ?
                "Escolha uma imagem de disco .cue ou .bin com seu CUE correspondente." :
                "Choose a .cue disc descriptor or a .bin with its companion CUE."
            throw LauncherError.message(msg)
        }
        let cueSize = try regularFile(cue)
        guard cueSize > 0 && cueSize <= 65_536 else {
            let msg = L10n.currentLanguage == .portuguese ?
                "O descritor CUE está vazio ou é grande demais para este formato." :
                "The CUE descriptor is empty or too large for this format."
            throw LauncherError.message(msg)
        }
        let bytes = try Data(contentsOf: cue)
        guard let source = String(data: bytes, encoding: .utf8) ?? String(data: bytes, encoding: .isoLatin1) else {
            let msg = L10n.currentLanguage == .portuguese ?
                "Não foi possível ler o texto do arquivo CUE." :
                "Could not parse text inside the CUE file."
            throw LauncherError.message(msg)
        }
        let lines = source.components(separatedBy: .newlines)
            .map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }
            .filter { !$0.isEmpty }
        let files = lines.filter { $0.uppercased().hasPrefix("FILE ") || $0.uppercased().hasPrefix("FILE\t") }
        let tracks = lines.filter { $0.uppercased().hasPrefix("TRACK ") || $0.uppercased().hasPrefix("TRACK\t") }
        let indexes = lines.filter { $0.uppercased().hasPrefix("INDEX ") || $0.uppercased().hasPrefix("INDEX\t") }
        guard files.count == 1, tracks.count == 1,
              capture(#"^TRACK\s+0?1\s+(CDI/2352|MODE2/2352)\s*$"#, tracks[0]) != nil,
              indexes.count == 1,
              capture(#"^INDEX\s+0?1\s+(00:00:00)\s*$"#, indexes[0]) != nil,
              !lines.contains(where: { $0.uppercased().hasPrefix("PREGAP") || $0.uppercased().hasPrefix("POSTGAP") }) else {
            let msg = L10n.currentLanguage == .portuguese ?
                "Este runtime aceita um CUE com uma única faixa CDI/2352 ou MODE2/2352, iniciando em INDEX 01 00:00:00, sem pregap." :
                "This runtime expects a CUE with a single CDI/2352 or MODE2/2352 track starting at INDEX 01 00:00:00 without pregap."
            throw LauncherError.message(msg)
        }
        let name = capture(#"^FILE\s+"([^"]+)"\s+BINARY\s*$"#, files[0]) ??
            capture(#"^FILE\s+(\S+)\s+BINARY\s*$"#, files[0])
        guard let filename = name, !filename.isEmpty,
              !filename.contains("/"), !filename.contains("\\"),
              filename != ".", filename != ".." else {
            let msg = L10n.currentLanguage == .portuguese ?
                "O CUE deve apontar para um único arquivo BIN na mesma pasta." :
                "The CUE must reference a single BIN file in the same directory."
            throw LauncherError.message(msg)
        }
        let bin = cue.deletingLastPathComponent().appendingPathComponent(filename)
        let binSize = try regularFile(bin)
        guard binSize > 0, binSize % 2352 == 0 else {
            let msg = L10n.currentLanguage == .portuguese ?
                "O BIN não contém uma quantidade inteira de setores de 2352 bytes ou está vazio." :
                "The BIN file does not contain a valid integer number of 2352-byte sectors."
            throw LauncherError.message(msg)
        }
        if selectedURL.pathExtension.lowercased() == "bin",
           selectedURL.resolvingSymlinksInPath().standardizedFileURL != bin.resolvingSymlinksInPath().standardizedFileURL {
            let msg = L10n.currentLanguage == .portuguese ?
                "O CUE encontrado aponta para outro BIN. Escolha diretamente o CUE correto." :
                "The companion CUE references a different BIN file. Select the matching CUE directly."
            throw LauncherError.message(msg)
        }
        return SelectedDisc(cue: cue, bin: bin)
    }

    private static func capture(_ pattern: String, _ text: String) -> String? {
        guard let regex = try? NSRegularExpression(pattern: pattern, options: [.caseInsensitive]),
              let match = regex.firstMatch(in: text, range: NSRange(text.startIndex..., in: text)),
              let range = Range(match.range(at: 1), in: text) else { return nil }
        return String(text[range])
    }

    static func sha256(_ url: URL, progress: (Double) -> Void) throws -> String {
        let length = try regularFile(url)
        let input = try FileHandle(forReadingFrom: url)
        defer { try? input.close() }
        var hasher = SHA256()
        var completed: Int64 = 0
        var lastUpdate = Date.distantPast
        while true {
            let chunk = try input.read(upToCount: 1_048_576) ?? Data()
            if chunk.isEmpty { break }
            hasher.update(data: chunk)
            completed += Int64(chunk.count)
            if Date().timeIntervalSince(lastUpdate) >= 0.1 {
                progress(length == 0 ? 1 : min(1, Double(completed) / Double(length)))
                lastUpdate = Date()
            }
        }
        guard completed == length else {
            let msg = L10n.currentLanguage == .portuguese ?
                "O arquivo mudou durante a verificação. Aguarde a cópia terminar e tente novamente." :
                "File changed during verification. Wait for file copy to finish and retry."
            throw LauncherError.message(msg)
        }
        progress(1)
        return hasher.finalize().map { String(format: "%02x", $0) }.joined()
    }

    static func bios(at selectedURL: URL, manifest: BIOSManifest, support: URL) throws -> URL {
        guard try regularFile(selectedURL) == manifest.size else {
            let msg = L10n.currentLanguage == .portuguese ?
                "Esta BIOS precisa ter exatamente \(manifest.size) bytes. Escolha a BIOS compatível com esta compilação." :
                "This BIOS file must be exactly \(manifest.size) bytes. Select the compatible BIOS revision."
            throw LauncherError.message(msg)
        }
        let digest = try sha256(selectedURL, progress: { _ in })
        let runtimeDigest = (manifest.runtimeSHA256 ?? manifest.sha256).lowercased()
        if digest == runtimeDigest { return selectedURL }
        guard digest == manifest.sha256.lowercased() else {
            let msg = L10n.currentLanguage == .portuguese ?
                "A BIOS selecionada pertence a outra revisão. Este aplicativo contém código recompilado para uma BIOS específica." :
                "Selected BIOS belongs to a different revision. This build requires the specific supported BIOS."
            throw LauncherError.message(msg)
        }
        guard manifest.byteOrder == "swap16", manifest.size % 2 == 0 else {
            let msg = L10n.currentLanguage == .portuguese ?
                "A ordem de bytes desta BIOS não é compatível com o runtime incluído." :
                "The byte order of this BIOS is incompatible with the bundled runtime."
            throw LauncherError.message(msg)
        }
        var firmware = try Data(contentsOf: selectedURL)
        guard firmware.count == Int(manifest.size) else {
            let msg = L10n.currentLanguage == .portuguese ?
                "A BIOS mudou durante a leitura. Escolha novamente o arquivo original." :
                "The BIOS changed while reading. Re-select the original file."
            throw LauncherError.message(msg)
        }
        firmware.withUnsafeMutableBytes { (buffer: UnsafeMutableRawBufferPointer) in
            for offset in stride(from: 0, to: buffer.count, by: 2) {
                let first = buffer[offset]
                buffer[offset] = buffer[offset + 1]
                buffer[offset + 1] = first
            }
        }
        let normalizedDigest = SHA256.hash(data: firmware).map { String(format: "%02x", $0) }.joined()
        guard normalizedDigest == runtimeDigest else {
            let msg = L10n.currentLanguage == .portuguese ?
                "A conversão da BIOS não corresponde à identidade exigida pelo runtime. A mídia original foi preservada." :
                "Normalized BIOS checksum does not match required runtime identity. Original media was preserved."
            throw LauncherError.message(msg)
        }
        let directory = support.appendingPathComponent("firmware", isDirectory: true)
        try fileManager.createDirectory(at: directory, withIntermediateDirectories: true,
                                       attributes: [.posixPermissions: 0o700])
        let output = directory.appendingPathComponent("cdi-\(runtimeDigest.prefix(16)).be.rom")
        try firmware.write(to: output, options: .atomic)
        try fileManager.setAttributes([.posixPermissions: 0o600], ofItemAtPath: output.path)
        return output
    }
}

// MARK: - Controls Window Sheet

private final class FlippedView: NSView {
    override var isFlipped: Bool { true }
}

private final class ControlsWindowController: NSWindowController {
    convenience init(parent: NSWindow) {
        let panel = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 640, height: 490),
                             styleMask: [.titled, .closable],
                             backing: .buffered, defer: false)
        panel.title = L10n.t("controls.title")
        panel.isReleasedWhenClosed = false
        self.init(window: panel)

        guard let contentView = panel.contentView else { return }

        // Main vertical container: Header (fixed) -> ScrollView (flex) -> Footer (fixed)
        let mainStack = NSStackView()
        mainStack.orientation = .vertical
        mainStack.alignment = .leading
        mainStack.spacing = 0
        mainStack.translatesAutoresizingMaskIntoConstraints = false
        contentView.addSubview(mainStack)
        NSLayoutConstraint.activate([
            mainStack.leadingAnchor.constraint(equalTo: contentView.leadingAnchor),
            mainStack.trailingAnchor.constraint(equalTo: contentView.trailingAnchor),
            mainStack.topAnchor.constraint(equalTo: contentView.topAnchor),
            mainStack.bottomAnchor.constraint(equalTo: contentView.bottomAnchor)
        ])

        // Top Header
        let headerView = NSView()
        headerView.translatesAutoresizingMaskIntoConstraints = false
        let titleLabel = NSTextField(labelWithString: L10n.t("controls.title"))
        titleLabel.font = .systemFont(ofSize: 20, weight: .bold)
        titleLabel.translatesAutoresizingMaskIntoConstraints = false
        headerView.addSubview(titleLabel)

        let subLabel = NSTextField(labelWithString: L10n.t("controls.subtitle"))
        subLabel.font = .systemFont(ofSize: 12)
        subLabel.textColor = .secondaryLabelColor
        subLabel.translatesAutoresizingMaskIntoConstraints = false
        headerView.addSubview(subLabel)

        let headerSeparator = NSBox()
        headerSeparator.boxType = .separator
        headerSeparator.translatesAutoresizingMaskIntoConstraints = false
        headerView.addSubview(headerSeparator)

        NSLayoutConstraint.activate([
            titleLabel.leadingAnchor.constraint(equalTo: headerView.leadingAnchor, constant: 24),
            titleLabel.trailingAnchor.constraint(equalTo: headerView.trailingAnchor, constant: -24),
            titleLabel.topAnchor.constraint(equalTo: headerView.topAnchor, constant: 18),

            subLabel.leadingAnchor.constraint(equalTo: titleLabel.leadingAnchor),
            subLabel.trailingAnchor.constraint(equalTo: titleLabel.trailingAnchor),
            subLabel.topAnchor.constraint(equalTo: titleLabel.bottomAnchor, constant: 4),

            headerSeparator.leadingAnchor.constraint(equalTo: headerView.leadingAnchor),
            headerSeparator.trailingAnchor.constraint(equalTo: headerView.trailingAnchor),
            headerSeparator.topAnchor.constraint(equalTo: subLabel.bottomAnchor, constant: 14),
            headerSeparator.bottomAnchor.constraint(equalTo: headerView.bottomAnchor)
        ])
        mainStack.addArrangedSubview(headerView)
        headerView.widthAnchor.constraint(equalTo: mainStack.widthAnchor).isActive = true

        // Scroll Area
        let scrollView = NSScrollView()
        scrollView.drawsBackground = false
        scrollView.hasVerticalScroller = true
        scrollView.hasHorizontalScroller = false
        scrollView.autohidesScrollers = true
        scrollView.translatesAutoresizingMaskIntoConstraints = false

        let documentView = FlippedView()
        documentView.translatesAutoresizingMaskIntoConstraints = false
        scrollView.documentView = documentView

        let scrollStack = NSStackView()
        scrollStack.orientation = .vertical
        scrollStack.alignment = .leading
        scrollStack.spacing = 14
        scrollStack.translatesAutoresizingMaskIntoConstraints = false
        documentView.addSubview(scrollStack)

        NSLayoutConstraint.activate([
            documentView.topAnchor.constraint(equalTo: scrollView.contentView.topAnchor),
            documentView.leadingAnchor.constraint(equalTo: scrollView.contentView.leadingAnchor),
            documentView.widthAnchor.constraint(equalTo: scrollView.contentView.widthAnchor),

            scrollStack.topAnchor.constraint(equalTo: documentView.topAnchor, constant: 14),
            scrollStack.leadingAnchor.constraint(equalTo: documentView.leadingAnchor, constant: 20),
            scrollStack.trailingAnchor.constraint(equalTo: documentView.trailingAnchor, constant: -20),
            scrollStack.bottomAnchor.constraint(equalTo: documentView.bottomAnchor, constant: -14)
        ])

        mainStack.addArrangedSubview(scrollView)
        scrollView.widthAnchor.constraint(equalTo: mainStack.widthAnchor).isActive = true

        // Helper: Badge de Tecla
        func makeKeyBadge(_ text: String) -> NSView {
            let container = NSView()
            container.wantsLayer = true
            container.layer?.cornerRadius = 5
            container.layer?.borderWidth = 1
            container.layer?.borderColor = NSColor.separatorColor.withAlphaComponent(0.5).cgColor
            container.layer?.backgroundColor = NSColor.controlBackgroundColor.cgColor
            container.translatesAutoresizingMaskIntoConstraints = false

            let label = NSTextField(labelWithString: text)
            label.font = .monospacedSystemFont(ofSize: 11.5, weight: .semibold)
            label.textColor = .systemBlue
            label.translatesAutoresizingMaskIntoConstraints = false
            container.addSubview(label)

            NSLayoutConstraint.activate([
                label.leadingAnchor.constraint(equalTo: container.leadingAnchor, constant: 8),
                label.trailingAnchor.constraint(equalTo: container.trailingAnchor, constant: -8),
                label.topAnchor.constraint(equalTo: container.topAnchor, constant: 4),
                label.bottomAnchor.constraint(equalTo: container.bottomAnchor, constant: -4)
            ])
            return container
        }

        // Helper: Linha de Tabela de Controles
        func makeControlRow(action: String, keyText: String) -> NSView {
            let row = NSView()
            row.translatesAutoresizingMaskIntoConstraints = false

            let actionLabel = NSTextField(labelWithString: action)
            actionLabel.font = .systemFont(ofSize: 12.5, weight: .medium)
            actionLabel.textColor = .labelColor
            actionLabel.setContentHuggingPriority(.required, for: .horizontal)
            actionLabel.translatesAutoresizingMaskIntoConstraints = false
            row.addSubview(actionLabel)

            let badge = makeKeyBadge(keyText)
            row.addSubview(badge)

            NSLayoutConstraint.activate([
                actionLabel.leadingAnchor.constraint(equalTo: row.leadingAnchor),
                actionLabel.centerYAnchor.constraint(equalTo: row.centerYAnchor),
                actionLabel.widthAnchor.constraint(equalToConstant: 230),

                badge.leadingAnchor.constraint(equalTo: actionLabel.trailingAnchor, constant: 12),
                badge.trailingAnchor.constraint(lessThanOrEqualTo: row.trailingAnchor),
                badge.topAnchor.constraint(equalTo: row.topAnchor),
                badge.bottomAnchor.constraint(equalTo: row.bottomAnchor),
                row.heightAnchor.constraint(greaterThanOrEqualToConstant: 26)
            ])
            return row
        }

        // Helper: Card estilizado
        func makeCard(title: String, rows: [(String, String)]) -> NSView {
            let card = NSView()
            card.wantsLayer = true
            card.layer?.cornerRadius = 10
            card.layer?.borderWidth = 1
            card.layer?.borderColor = NSColor.separatorColor.withAlphaComponent(0.5).cgColor
            card.layer?.backgroundColor = NSColor.controlBackgroundColor.withAlphaComponent(0.4).cgColor
            card.translatesAutoresizingMaskIntoConstraints = false

            let cardStack = NSStackView()
            cardStack.orientation = .vertical
            cardStack.alignment = .leading
            cardStack.spacing = 10
            cardStack.translatesAutoresizingMaskIntoConstraints = false
            card.addSubview(cardStack)

            let cardTitle = NSTextField(labelWithString: title)
            cardTitle.font = .systemFont(ofSize: 13.5, weight: .bold)
            cardTitle.textColor = .labelColor
            cardStack.addArrangedSubview(cardTitle)

            for (action, key) in rows {
                let rowView = makeControlRow(action: action, keyText: key)
                cardStack.addArrangedSubview(rowView)
                rowView.widthAnchor.constraint(equalTo: cardStack.widthAnchor).isActive = true
            }

            NSLayoutConstraint.activate([
                cardStack.leadingAnchor.constraint(equalTo: card.leadingAnchor, constant: 16),
                cardStack.trailingAnchor.constraint(equalTo: card.trailingAnchor, constant: -16),
                cardStack.topAnchor.constraint(equalTo: card.topAnchor, constant: 14),
                cardStack.bottomAnchor.constraint(equalTo: card.bottomAnchor, constant: -14)
            ])
            return card
        }

        // 1. Teclado
        let kbCard = makeCard(title: L10n.t("controls.keyboard"), rows: [
            (L10n.t("controls.movement"), L10n.t("controls.movement_desc")),
            (L10n.t("controls.btn1"), L10n.t("controls.btn1_desc")),
            (L10n.t("controls.btn2"), L10n.t("controls.btn2_desc")),
            (L10n.t("controls.fullscreen"), L10n.t("controls.fullscreen_desc")),
            (L10n.t("controls.exit"), L10n.t("controls.exit_desc"))
        ])
        scrollStack.addArrangedSubview(kbCard)
        kbCard.widthAnchor.constraint(equalTo: scrollStack.widthAnchor).isActive = true

        // 2. Gamepad
        let gpCard = makeCard(title: L10n.t("controls.gamepad"), rows: [
            (L10n.t("controls.gamepad_dpad"), L10n.t("controls.gamepad_dpad_desc")),
            (L10n.t("controls.gamepad_a"), L10n.t("controls.gamepad_a_desc")),
            (L10n.t("controls.gamepad_b"), L10n.t("controls.gamepad_b_desc"))
        ])
        scrollStack.addArrangedSubview(gpCard)
        gpCard.widthAnchor.constraint(equalTo: scrollStack.widthAnchor).isActive = true

        // 3. Mouse
        let mouseCard = NSView()
        mouseCard.wantsLayer = true
        mouseCard.layer?.cornerRadius = 10
        mouseCard.layer?.borderWidth = 1
        mouseCard.layer?.borderColor = NSColor.separatorColor.withAlphaComponent(0.5).cgColor
        mouseCard.layer?.backgroundColor = NSColor.controlBackgroundColor.withAlphaComponent(0.4).cgColor
        mouseCard.translatesAutoresizingMaskIntoConstraints = false

        let mouseStack = NSStackView()
        mouseStack.orientation = .vertical
        mouseStack.alignment = .leading
        mouseStack.spacing = 8
        mouseStack.translatesAutoresizingMaskIntoConstraints = false
        mouseCard.addSubview(mouseStack)

        let mouseTitle = NSTextField(labelWithString: L10n.t("controls.mouse"))
        mouseTitle.font = .systemFont(ofSize: 13.5, weight: .bold)
        mouseTitle.textColor = .labelColor
        mouseStack.addArrangedSubview(mouseTitle)

        let mouseDesc = NSTextField(wrappingLabelWithString: L10n.t("controls.mouse_desc"))
        mouseDesc.font = .systemFont(ofSize: 12)
        mouseDesc.textColor = .secondaryLabelColor
        mouseStack.addArrangedSubview(mouseDesc)

        NSLayoutConstraint.activate([
            mouseStack.leadingAnchor.constraint(equalTo: mouseCard.leadingAnchor, constant: 16),
            mouseStack.trailingAnchor.constraint(equalTo: mouseCard.trailingAnchor, constant: -16),
            mouseStack.topAnchor.constraint(equalTo: mouseCard.topAnchor, constant: 14),
            mouseStack.bottomAnchor.constraint(equalTo: mouseCard.bottomAnchor, constant: -14)
        ])
        scrollStack.addArrangedSubview(mouseCard)
        mouseCard.widthAnchor.constraint(equalTo: scrollStack.widthAnchor).isActive = true

        // Bottom Footer
        let footerView = NSView()
        footerView.translatesAutoresizingMaskIntoConstraints = false

        let footerSeparator = NSBox()
        footerSeparator.boxType = .separator
        footerSeparator.translatesAutoresizingMaskIntoConstraints = false
        footerView.addSubview(footerSeparator)

        let footerContent = NSStackView()
        footerContent.orientation = .horizontal
        footerContent.alignment = .centerY
        footerContent.spacing = 12
        footerContent.translatesAutoresizingMaskIntoConstraints = false
        footerView.addSubview(footerContent)

        let prefLabel = NSTextField(labelWithString: L10n.t("controls.pref_label"))
        prefLabel.font = .systemFont(ofSize: 12, weight: .medium)
        footerContent.addArrangedSubview(prefLabel)

        let schemePopup = NSPopUpButton()
        schemePopup.addItems(withTitles: [
            L10n.t("controls.pref_opt1"),
            L10n.t("controls.pref_opt2")
        ])
        let savedIndex = UserDefaults.standard.integer(forKey: "keyboardSchemeIndex")
        if savedIndex < schemePopup.numberOfItems {
            schemePopup.selectItem(at: savedIndex)
        }
        schemePopup.target = self
        schemePopup.action = #selector(schemeChanged(_:))
        footerContent.addArrangedSubview(schemePopup)

        let spacer = NSView()
        footerContent.addArrangedSubview(spacer)

        let doneBtn = NSButton(title: L10n.t("btn.close"), target: self, action: #selector(closeSheet))
        doneBtn.bezelStyle = .rounded
        doneBtn.keyEquivalent = "\r"
        footerContent.addArrangedSubview(doneBtn)

        NSLayoutConstraint.activate([
            footerSeparator.leadingAnchor.constraint(equalTo: footerView.leadingAnchor),
            footerSeparator.trailingAnchor.constraint(equalTo: footerView.trailingAnchor),
            footerSeparator.topAnchor.constraint(equalTo: footerView.topAnchor),

            footerContent.leadingAnchor.constraint(equalTo: footerView.leadingAnchor, constant: 24),
            footerContent.trailingAnchor.constraint(equalTo: footerView.trailingAnchor, constant: -24),
            footerContent.topAnchor.constraint(equalTo: footerSeparator.bottomAnchor, constant: 14),
            footerContent.bottomAnchor.constraint(equalTo: footerView.bottomAnchor, constant: -16)
        ])

        mainStack.addArrangedSubview(footerView)
        footerView.widthAnchor.constraint(equalTo: mainStack.widthAnchor).isActive = true
    }

    @objc private func schemeChanged(_ sender: NSPopUpButton) {
        UserDefaults.standard.set(sender.indexOfSelectedItem, forKey: "keyboardSchemeIndex")
    }

    @objc private func closeSheet() {
        if let window = window, let sheetParent = window.sheetParent {
            sheetParent.endSheet(window)
        } else {
            window?.close()
        }
    }

    override func cancelOperation(_ sender: Any?) {
        closeSheet()
    }
}

// MARK: - Main Application Delegate & Launcher

private final class LauncherDelegate: NSObject, NSApplicationDelegate, NSTableViewDataSource, NSTableViewDelegate, NSWindowDelegate {
    private let fileManager = FileManager.default
    private let defaults = UserDefaults.standard
    private let worker = DispatchQueue(label: "org.zeldacdi.launcher.media", qos: .userInitiated)
    private var manifest: RuntimeManifest?
    private var manifestFailure: String?
    private var window: NSWindow!
    private var table: NSTableView!
    private let gameTitle = NSTextField(labelWithString: "Zelda CD-i")
    private let gameStatus = NSTextField(wrappingLabelWithString: "")
    private let biosPath = NSTextField(labelWithString: "")
    private let discPath = NSTextField(labelWithString: "")
    private let status = NSTextField(wrappingLabelWithString: "")
    private let progress = NSProgressIndicator()
    private var biosLabel: NSTextField!
    private var discLabel: NSTextField!
    private var biosHint: NSTextField!
    private var discHint: NSTextField!
    private var biosButton: NSButton!
    private var discButton: NSButton!
    private var playButton: NSButton!
    private var stopButton: NSButton!
    private var controlsButton: NSButton!
    private var logButton: NSButton!
    private var subtitleLabel: NSTextField!
    private var libraryLabel: NSTextField!
    private var footerNote: NSTextField!
    private var languageSelector: NSPopUpButton!

    private var busy = false
    private var process: Process?
    private var logHandle: FileHandle?
    private var latestLog: URL?
    private var pendingTermination = false
    private var selectedIndex = 0
    private var controlsController: ControlsWindowController?

    private var selectedGame: GameManifest? {
        guard let games = manifest?.games, games.indices.contains(selectedIndex) else { return nil }
        return games[selectedIndex]
    }

    private var supportDirectory: URL {
        fileManager.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0]
            .appendingPathComponent("ZeldaCDiNative", isDirectory: true)
    }

    func applicationDidFinishLaunching(_ notification: Notification) {
        if let iconURL = Bundle.main.url(forResource: "AppIcon", withExtension: "icns"),
           let img = NSImage(contentsOf: iconURL) {
            NSApp.applicationIconImage = img
        }
        loadManifest()
        buildMenu()
        buildWindow()
        autodetectLocalMedia()
        if let games = manifest?.games, !games.isEmpty {
            let previous = defaults.string(forKey: "selectedGame")
            selectedIndex = games.firstIndex(where: { $0.id == previous }) ?? 0
            table.selectRowIndexes(IndexSet(integer: selectedIndex), byExtendingSelection: false)
        }
        applyLanguage()
        window.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
        if let failure = manifestFailure {
            status.stringValue = L10n.currentLanguage == .portuguese ?
                "Aplicativo incompleto. Consulte a mensagem de instalação." :
                "Incomplete application. Check bundle installation."
            showError(failure, title: L10n.currentLanguage == .portuguese ?
                "Não foi possível carregar o aplicativo" : "Unable to load application")
        }
    }

    private func loadManifest() {
        do {
            guard let url = Bundle.main.url(forResource: "runtime-manifest", withExtension: "json") else {
                let msg = L10n.currentLanguage == .portuguese ?
                    "O manifesto dos runtimes não está no aplicativo. Gere novamente o pacote .app completo." :
                    "Runtime manifest missing from app bundle. Rebuild the .app package."
                throw LauncherError.message(msg)
            }
            let decoded = try JSONDecoder().decode(RuntimeManifest.self, from: Data(contentsOf: url))
            guard decoded.schemaVersion == 1, !decoded.games.isEmpty,
                  decoded.bios.size > 0, validDigest(decoded.bios.sha256),
                  decoded.bios.runtimeSHA256.map(validDigest) ?? true,
                  decoded.bios.byteOrder == nil || decoded.bios.byteOrder == "swap16",
                  Set(decoded.games.map(\.id)).count == decoded.games.count else {
                let msg = L10n.currentLanguage == .portuguese ?
                    "O manifesto do aplicativo tem uma versão ou identidade de mídia inválida." :
                    "Application manifest has an invalid version or media identity."
                throw LauncherError.message(msg)
            }
            for game in decoded.games {
                guard game.id.range(of: #"^[a-z0-9_-]+$"#, options: .regularExpression) != nil,
                      game.runtime.range(of: #"^[A-Za-z0-9][A-Za-z0-9._-]*$"#, options: .regularExpression) != nil,
                      validDigest(game.discSHA256), !game.title.isEmpty else {
                    let msg = L10n.currentLanguage == .portuguese ?
                        "O manifesto contém um caminho ou jogo inválido." :
                        "Manifest contains an invalid runtime path or game entry."
                    throw LauncherError.message(msg)
                }
            }
            manifest = decoded
        } catch { manifestFailure = error.localizedDescription }
    }

    private func validDigest(_ value: String) -> Bool {
        value.range(of: #"^[0-9a-fA-F]{64}$"#, options: .regularExpression) != nil
    }

    private func buildMenu() {
        let menu = NSMenu()
        let appMenu = NSMenu()
        let root = NSMenuItem()
        root.submenu = appMenu
        menu.addItem(root)
        appMenu.addItem(withTitle: L10n.t("menu.about"), action: #selector(showAbout), keyEquivalent: "")
        appMenu.addItem(NSMenuItem.separator())
        appMenu.addItem(withTitle: L10n.t("menu.hide"), action: #selector(NSApplication.hide(_:)), keyEquivalent: "h")
        appMenu.addItem(withTitle: L10n.t("menu.quit"), action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q")

        // File Menu
        let fileRoot = NSMenuItem(title: L10n.t("menu.file"), action: nil, keyEquivalent: "")
        let fileMenu = NSMenu(title: L10n.t("menu.file"))
        fileMenu.addItem(withTitle: L10n.t("menu.choose_disc"), action: #selector(chooseDisc), keyEquivalent: "o")
        fileMenu.addItem(withTitle: L10n.t("menu.open_log"), action: #selector(openLog), keyEquivalent: "l")
        fileMenu.addItem(withTitle: L10n.t("menu.open_data"), action: #selector(openSupport), keyEquivalent: "")
        fileRoot.submenu = fileMenu
        menu.addItem(fileRoot)

        // Language Menu
        let langRoot = NSMenuItem(title: L10n.t("menu.language"), action: nil, keyEquivalent: "")
        let langMenu = NSMenu(title: L10n.t("menu.language"))
        for lang in AppLanguage.allCases {
            let item = NSMenuItem(title: lang.displayName, action: #selector(changeLanguageFromMenu(_:)), keyEquivalent: "")
            item.representedObject = lang
            item.state = (lang == L10n.currentLanguage) ? .on : .off
            langMenu.addItem(item)
        }
        langRoot.submenu = langMenu
        menu.addItem(langRoot)

        // Help Menu
        let helpRoot = NSMenuItem(title: L10n.t("menu.help"), action: nil, keyEquivalent: "")
        let helpMenu = NSMenu(title: L10n.t("menu.help"))
        helpMenu.addItem(withTitle: L10n.t("menu.controls"), action: #selector(showControls), keyEquivalent: "k")
        helpRoot.submenu = helpMenu
        menu.addItem(helpRoot)

        NSApp.mainMenu = menu
    }

    private func buildWindow() {
        window = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 920, height: 580),
                          styleMask: [.titled, .closable, .miniaturizable, .resizable],
                          backing: .buffered, defer: false)
        let version = Bundle.main.object(forInfoDictionaryKey: "CFBundleShortVersionString") as? String ?? "dev"
        window.title = "Zelda CD-i — \(version)"
        window.minSize = NSSize(width: 820, height: 530)
        window.center()
        window.delegate = self
        window.isReleasedWhenClosed = false

        let root = NSStackView()
        root.orientation = .vertical
        root.alignment = .leading
        root.spacing = 18
        root.translatesAutoresizingMaskIntoConstraints = false
        window.contentView!.addSubview(root)
        NSLayoutConstraint.activate([
            root.leadingAnchor.constraint(equalTo: window.contentView!.leadingAnchor, constant: 26),
            root.trailingAnchor.constraint(equalTo: window.contentView!.trailingAnchor, constant: -26),
            root.topAnchor.constraint(equalTo: window.contentView!.topAnchor, constant: 22),
            root.bottomAnchor.constraint(equalTo: window.contentView!.bottomAnchor, constant: -20)
        ])

        // Header with title and language selector
        let topBar = NSStackView()
        topBar.orientation = .horizontal
        topBar.alignment = .centerY
        topBar.spacing = 16

        let header = NSStackView()
        header.orientation = .vertical
        header.alignment = .leading
        header.spacing = 4
        let title = NSTextField(labelWithString: "Zelda CD-i")
        title.font = .systemFont(ofSize: 28, weight: .bold)
        header.addArrangedSubview(title)
        subtitleLabel = NSTextField(labelWithString: L10n.t("app.subtitle"))
        subtitleLabel.textColor = .secondaryLabelColor
        subtitleLabel.font = .systemFont(ofSize: 13)
        header.addArrangedSubview(subtitleLabel)
        topBar.addArrangedSubview(header)

        let topSpacer = NSView()
        topBar.addArrangedSubview(topSpacer)

        // Language PopUp
        let langStack = NSStackView()
        langStack.orientation = .horizontal
        langStack.spacing = 6
        languageSelector = NSPopUpButton()
        for lang in AppLanguage.allCases {
            languageSelector.addItem(withTitle: lang.flagTitle)
        }
        if let idx = AppLanguage.allCases.firstIndex(of: L10n.currentLanguage) {
            languageSelector.selectItem(at: idx)
        }
        languageSelector.toolTip = "Idioma da interface e do próximo jogo. Tradução parcial: slots vazios e botões do menu de Adventure. Reinicie o jogo após mudar. / Interface and next game language; restart the game to apply."
        languageSelector.target = self
        languageSelector.action = #selector(languageSelected(_:))
        langStack.addArrangedSubview(languageSelector)
        topBar.addArrangedSubview(langStack)

        root.addArrangedSubview(topBar)
        topBar.widthAnchor.constraint(equalTo: root.widthAnchor).isActive = true

        let body = NSStackView()
        body.orientation = .horizontal
        body.alignment = .top
        body.spacing = 24
        root.addArrangedSubview(body)
        body.widthAnchor.constraint(equalTo: root.widthAnchor).isActive = true

        let library = NSStackView()
        library.orientation = .vertical
        library.alignment = .leading
        library.spacing = 10
        libraryLabel = NSTextField(labelWithString: L10n.t("app.library_title"))
        libraryLabel.font = .systemFont(ofSize: 11, weight: .semibold)
        libraryLabel.textColor = .secondaryLabelColor
        library.addArrangedSubview(libraryLabel)
        let scroll = NSScrollView()
        scroll.hasVerticalScroller = true
        scroll.borderType = .lineBorder
        table = NSTableView()
        let column = NSTableColumn(identifier: NSUserInterfaceItemIdentifier("game"))
        column.width = 255
        table.addTableColumn(column)
        table.headerView = nil
        table.rowHeight = 65
        table.intercellSpacing = NSSize(width: 0, height: 2)
        table.style = .sourceList
        table.dataSource = self
        table.delegate = self
        table.allowsEmptySelection = false
        table.allowsMultipleSelection = false
        scroll.documentView = table
        library.addArrangedSubview(scroll)
        scroll.widthAnchor.constraint(equalToConstant: 260).isActive = true
        scroll.heightAnchor.constraint(greaterThanOrEqualToConstant: 265).isActive = true
        scroll.widthAnchor.constraint(equalTo: library.widthAnchor).isActive = true
        body.addArrangedSubview(library)

        let detail = NSStackView()
        detail.orientation = .vertical
        detail.alignment = .leading
        detail.spacing = 14
        body.addArrangedSubview(detail)
        detail.setContentHuggingPriority(.defaultLow, for: .horizontal)
        gameTitle.font = .systemFont(ofSize: 21, weight: .semibold)
        gameTitle.maximumNumberOfLines = 2
        detail.addArrangedSubview(gameTitle)
        gameStatus.font = .systemFont(ofSize: 12)
        gameStatus.textColor = .secondaryLabelColor
        gameStatus.maximumNumberOfLines = 4
        detail.addArrangedSubview(gameStatus)
        gameStatus.widthAnchor.constraint(equalTo: detail.widthAnchor).isActive = true

        let biosRow = makeMediaRow(title: L10n.t("media.bios_title"), hintText: L10n.t("media.bios_hint"), path: biosPath, selector: #selector(chooseBIOS), isBIOS: true)
        detail.addArrangedSubview(biosRow)
        let discRow = makeMediaRow(title: L10n.t("media.disc_title"), hintText: L10n.t("media.disc_hint"), path: discPath, selector: #selector(chooseDisc), isBIOS: false)
        detail.addArrangedSubview(discRow)

        let controls = NSStackView()
        controls.orientation = .horizontal
        controls.spacing = 10
        playButton = NSButton(title: L10n.t("btn.start"), target: self, action: #selector(startGame))
        playButton.bezelStyle = .rounded
        playButton.keyEquivalent = "\r"

        stopButton = NSButton(title: L10n.t("btn.stop"), target: self, action: #selector(stopGame))
        stopButton.bezelStyle = .rounded

        controlsButton = NSButton(title: L10n.t("btn.controls"), target: self, action: #selector(showControls))
        controlsButton.bezelStyle = .rounded

        controls.addArrangedSubview(playButton)
        controls.addArrangedSubview(stopButton)
        controls.addArrangedSubview(controlsButton)
        detail.addArrangedSubview(controls)

        for item in detail.arrangedSubviews where item !== controls {
            item.widthAnchor.constraint(equalTo: detail.widthAnchor).isActive = true
        }
        detail.widthAnchor.constraint(greaterThanOrEqualToConstant: 440).isActive = true

        let divider = NSBox()
        divider.boxType = .separator
        root.addArrangedSubview(divider)
        divider.widthAnchor.constraint(equalTo: root.widthAnchor).isActive = true

        let footer = NSStackView()
        footer.orientation = .horizontal
        footer.alignment = .centerY
        footer.spacing = 12
        progress.style = .spinning
        progress.isDisplayedWhenStopped = false
        progress.controlSize = .small
        footer.addArrangedSubview(progress)
        status.font = .systemFont(ofSize: 12)
        status.maximumNumberOfLines = 3
        status.setContentHuggingPriority(.defaultLow, for: .horizontal)
        footer.addArrangedSubview(status)
        logButton = NSButton(title: L10n.t("btn.open_log"), target: self, action: #selector(openLog))
        logButton.bezelStyle = .rounded
        footer.addArrangedSubview(logButton)
        root.addArrangedSubview(footer)
        footer.widthAnchor.constraint(equalTo: root.widthAnchor).isActive = true

        footerNote = NSTextField(wrappingLabelWithString: L10n.t("app.note"))
        footerNote.font = .systemFont(ofSize: 11)
        footerNote.textColor = .secondaryLabelColor
        root.addArrangedSubview(footerNote)
        footerNote.widthAnchor.constraint(equalTo: root.widthAnchor).isActive = true
    }

    private func makeMediaRow(title: String, hintText: String, path: NSTextField, selector: Selector, isBIOS: Bool) -> NSView {
        let group = NSStackView()
        group.orientation = .vertical
        group.alignment = .leading
        group.spacing = 3
        let label = NSTextField(labelWithString: title)
        label.font = .systemFont(ofSize: 12, weight: .semibold)
        group.addArrangedSubview(label)
        if isBIOS { biosLabel = label } else { discLabel = label }

        let hint = NSTextField(labelWithString: hintText)
        hint.font = .systemFont(ofSize: 11)
        hint.textColor = .tertiaryLabelColor
        group.addArrangedSubview(hint)
        if isBIOS { biosHint = hint } else { discHint = hint }

        let row = NSStackView()
        row.orientation = .horizontal
        row.spacing = 8
        path.font = .systemFont(ofSize: 12)
        path.textColor = .secondaryLabelColor
        path.lineBreakMode = .byTruncatingMiddle
        path.isSelectable = true
        path.setContentCompressionResistancePriority(.defaultLow, for: .horizontal)
        path.setContentHuggingPriority(.defaultLow, for: .horizontal)
        row.addArrangedSubview(path)

        let button = NSButton(title: L10n.t("media.choose_button"), target: self, action: selector)
        button.bezelStyle = .rounded
        row.addArrangedSubview(button)
        if isBIOS { biosButton = button } else { discButton = button }

        group.addArrangedSubview(row)
        row.widthAnchor.constraint(equalTo: group.widthAnchor).isActive = true
        return group
    }

    private func applyLanguage() {
        subtitleLabel?.stringValue = L10n.t("app.subtitle")
        libraryLabel?.stringValue = L10n.t("app.library_title")
        biosLabel?.stringValue = L10n.t("media.bios_title")
        discLabel?.stringValue = L10n.t("media.disc_title")
        biosHint?.stringValue = L10n.t("media.bios_hint")
        discHint?.stringValue = L10n.t("media.disc_hint")
        biosButton?.title = L10n.t("media.choose_button")
        discButton?.title = L10n.t("media.choose_button")
        playButton?.title = L10n.t("btn.start")
        stopButton?.title = L10n.t("btn.stop")
        controlsButton?.title = L10n.t("btn.controls")
        logButton?.title = L10n.t("btn.open_log")
        footerNote?.stringValue = L10n.t("app.note")
        buildMenu()
        table?.reloadData()
        refreshSelection()
    }

    @objc private func languageSelected(_ sender: NSPopUpButton) {
        let index = sender.indexOfSelectedItem
        if index >= 0 && index < AppLanguage.allCases.count {
            L10n.currentLanguage = AppLanguage.allCases[index]
            applyLanguage()
        }
    }

    @objc private func changeLanguageFromMenu(_ sender: NSMenuItem) {
        if let lang = sender.representedObject as? AppLanguage {
            L10n.currentLanguage = lang
            if let idx = AppLanguage.allCases.firstIndex(of: lang) {
                languageSelector?.selectItem(at: idx)
            }
            applyLanguage()
        }
    }

    @objc private func showControls() {
        controlsController = ControlsWindowController(parent: window)
        if let sheet = controlsController?.window {
            window.beginSheet(sheet)
        }
    }

    private func autodetectLocalMedia() {
        guard let manifest = manifest else { return }

        // Localiza raízes candidatas para busca de arquivos:
        // 1. Pasta pai onde o .app reside (para pacotes zip e instalações portáteis)
        let bundleFolder = Bundle.main.bundleURL.deletingLastPathComponent().standardizedFileURL
        var candidateRoots = [bundleFolder]
        if let resources = Bundle.main.resourceURL {
            candidateRoots.insert(resources.appendingPathComponent("LocalMedia", isDirectory: true), at: 0)
        }

        // 2. Se houver rootPath configurado no manifesto, adiciona como fallback
        if let rootPath = manifest.localMediaRoot {
            candidateRoots.append(URL(fileURLWithPath: rootPath, isDirectory: true).standardizedFileURL)
        }

        func findReadableRelative(_ relative: String?) -> String? {
            guard let relative = relative, !relative.hasPrefix("/") else { return nil }
            for root in candidateRoots {
                let candidate = root.appendingPathComponent(relative).standardizedFileURL
                if fileManager.isReadableFile(atPath: candidate.path) {
                    return candidate.path
                }
            }
            return nil
        }

        // Valida se a BIOS salva em defaults ainda existe nesta máquina; se não existir, limpa
        if let savedBios = defaults.string(forKey: "biosPath") {
            if !fileManager.isReadableFile(atPath: savedBios) {
                defaults.removeObject(forKey: "biosPath")
            }
        }
        if defaults.string(forKey: "biosPath") == nil, let path = findReadableRelative(manifest.bios.localRelative) {
            defaults.set(path, forKey: "biosPath")
        }

        // Valida para cada jogo se o disco salvo em defaults existe; se não existir, limpa e tenta autodetectar
        for game in manifest.games {
            let key = discKey(game)
            if let savedDisc = defaults.string(forKey: key) {
                if !fileManager.isReadableFile(atPath: savedDisc) {
                    defaults.removeObject(forKey: key)
                }
            }
            if defaults.string(forKey: key) == nil, let path = findReadableRelative(game.localCueRelative) {
                defaults.set(path, forKey: key)
            }
        }
    }

    private func discKey(_ game: GameManifest) -> String { "discPath.\(game.id)" }

    private func refreshSelection() {
        guard let game = selectedGame else {
            gameStatus.stringValue = L10n.currentLanguage == .portuguese ?
                "Nenhum runtime disponível nesta instalação." : "No runtime available in this installation."
            updateControls()
            return
        }
        defaults.set(game.id, forKey: "selectedGame")
        gameTitle.stringValue = game.title

        let localizedStatusText = (game.statusText == "Em teste") ? L10n.t("status.testing") :
            ((game.statusText == "Ainda indisponível") ? L10n.t("status.unavailable") : game.statusText)
        gameStatus.stringValue = "\(localizedStatusText). \(L10n.t("status.compatibility_note"))"

        let bios = defaults.string(forKey: "biosPath")
        let disc = defaults.string(forKey: discKey(game))
        biosPath.stringValue = bios ?? L10n.t("media.no_bios")
        biosPath.toolTip = bios
        discPath.stringValue = disc ?? L10n.t("media.no_disc")
        discPath.toolTip = disc

        if !busy && process == nil {
            status.stringValue = "\(game.title) \(L10n.t("status.selected"))"
        }
        updateControls()
    }

    private func updateControls() {
        let idle = !busy && process == nil
        table?.isEnabled = idle
        biosButton?.isEnabled = idle && manifest != nil
        discButton?.isEnabled = idle && selectedGame != nil
        playButton?.isEnabled = idle && selectedGame != nil && defaults.string(forKey: "biosPath") != nil &&
            selectedGame.flatMap { defaults.string(forKey: discKey($0)) } != nil
        stopButton?.isEnabled = process?.isRunning == true
        controlsButton?.isEnabled = true
        logButton?.isEnabled = latestLog != nil
        if busy { progress.startAnimation(nil) } else { progress.stopAnimation(nil) }
    }

    func numberOfRows(in tableView: NSTableView) -> Int { manifest?.games.count ?? 0 }

    func tableView(_ tableView: NSTableView, viewFor tableColumn: NSTableColumn?, row: Int) -> NSView? {
        guard let games = manifest?.games, games.indices.contains(row) else { return nil }
        let game = games[row]
        let cell = NSTableCellView()
        let text = NSTextField(labelWithString: game.title)
        text.font = .systemFont(ofSize: 12, weight: .medium)
        text.lineBreakMode = .byTruncatingTail

        let localizedStatus = (game.statusText == "Em teste") ? L10n.t("status.testing") :
            ((game.statusText == "Ainda indisponível") ? L10n.t("status.unavailable") : game.statusText)
        let state = NSTextField(labelWithString: localizedStatus)
        state.font = .systemFont(ofSize: 11)
        state.textColor = .secondaryLabelColor

        let stack = NSStackView(views: [text, state])
        stack.orientation = .vertical
        stack.alignment = .leading
        stack.spacing = 4
        stack.translatesAutoresizingMaskIntoConstraints = false
        cell.addSubview(stack)
        NSLayoutConstraint.activate([
            stack.leadingAnchor.constraint(equalTo: cell.leadingAnchor, constant: 9),
            stack.trailingAnchor.constraint(equalTo: cell.trailingAnchor, constant: -8),
            stack.centerYAnchor.constraint(equalTo: cell.centerYAnchor)
        ])
        cell.textField = text
        return cell
    }

    func tableViewSelectionDidChange(_ notification: Notification) {
        guard !busy && process == nil, table.selectedRow >= 0 else { return }
        selectedIndex = table.selectedRow
        refreshSelection()
    }

    @objc private func chooseBIOS() {
        guard !busy && process == nil, manifest != nil else { return }
        let panel = NSOpenPanel()
        panel.title = L10n.t("media.bios_title")
        panel.message = L10n.t("media.panel_bios_msg")
        panel.prompt = L10n.t("media.panel_select")
        panel.canChooseDirectories = false
        panel.allowsMultipleSelection = false
        if #available(macOS 12.0, *) {
            // allows any file or rom/bin
        } else {
            panel.allowedFileTypes = ["rom", "bin"]
        }
        if let path = defaults.string(forKey: "biosPath") {
            panel.directoryURL = URL(fileURLWithPath: path).deletingLastPathComponent()
        }
        panel.beginSheetModal(for: window) { [weak self] result in
            guard let self = self, result == .OK, let url = panel.url else { return }
            self.defaults.set(url.path, forKey: "biosPath")
            self.refreshSelection()
        }
    }

    @objc private func chooseDisc() {
        guard !busy && process == nil, let game = selectedGame else { return }
        let panel = NSOpenPanel()
        panel.title = "\(L10n.t("media.disc_title")) — \(game.title)"
        panel.message = "\(L10n.t("media.panel_disc_msg")) (\(game.title))"
        panel.prompt = L10n.t("media.panel_select")
        panel.canChooseDirectories = false
        panel.allowsMultipleSelection = false
        if #available(macOS 12.0, *) {
            // allows any file or cue/bin
        } else {
            panel.allowedFileTypes = ["cue", "bin"]
        }
        if let path = defaults.string(forKey: discKey(game)) {
            panel.directoryURL = URL(fileURLWithPath: path).deletingLastPathComponent()
        }
        panel.beginSheetModal(for: window) { [weak self] result in
            guard let self = self, result == .OK, let url = panel.url else { return }
            do {
                let disc = try MediaValidator.disc(at: url)
                self.defaults.set(disc.cue.path, forKey: self.discKey(game))
                self.refreshSelection()
            } catch {
                let errTitle = L10n.currentLanguage == .portuguese ? "Disco incompatível" : "Incompatible Disc"
                self.showError(error.localizedDescription, title: errTitle)
            }
        }
    }

    @objc private func startGame() {
        guard !busy, process == nil, let manifest = manifest, let game = selectedGame,
              let bios = defaults.string(forKey: "biosPath"),
              let disc = defaults.string(forKey: discKey(game)) else { return }
        let runtime = Bundle.main.bundleURL.appendingPathComponent("Contents/MacOS").appendingPathComponent(game.runtime)
        guard fileManager.isExecutableFile(atPath: runtime.path) else {
            let msg = L10n.currentLanguage == .portuguese ?
                "O runtime de \(game.title) não está incluído ou não pode ser executado. Gere novamente o pacote completo." :
                "Runtime executable for \(game.title) is missing or not executable. Rebuild package."
            let errTitle = L10n.currentLanguage == .portuguese ? "Runtime indisponível" : "Runtime unavailable"
            showError(msg, title: errTitle)
            return
        }
        busy = true
        status.stringValue = L10n.t("status.verifying_bios")
        updateControls()
        let support = supportDirectory
        worker.async { [weak self] in
            guard let self = self else { return }
            do {
                let biosURL = try MediaValidator.bios(at: URL(fileURLWithPath: bios), manifest: manifest.bios, support: support)
                let selectedDisc = try MediaValidator.disc(at: URL(fileURLWithPath: disc))
                let digest = try MediaValidator.sha256(selectedDisc.bin) { fraction in
                    DispatchQueue.main.async { [weak self] in
                        self?.status.stringValue = "\(L10n.t("status.verifying_disc")) \(game.title)… \(Int(fraction * 100))%"
                    }
                }
                guard digest == game.discSHA256.lowercased() else {
                    let msg = L10n.currentLanguage == .portuguese ?
                        "O disco não corresponde à revisão recompilada de \(game.title). Escolha o BIN/CUE usado para gerar este aplicativo." :
                        "Disc checksum does not match the recompiled revision of \(game.title). Select matching BIN/CUE."
                    throw LauncherError.message(msg)
                }
                let gameData = support.appendingPathComponent(game.id, isDirectory: true)
                try self.fileManager.createDirectory(at: gameData, withIntermediateDirectories: true,
                                                     attributes: [.posixPermissions: 0o700])
                DispatchQueue.main.async { [weak self] in
                    self?.launch(game: game, runtime: runtime, bios: biosURL, disc: selectedDisc, gameData: gameData)
                }
            } catch {
                DispatchQueue.main.async { [weak self] in
                    guard let self = self else { return }
                    self.busy = false
                    self.status.stringValue = L10n.t("status.failed_verification")
                    self.updateControls()
                    let errTitle = L10n.currentLanguage == .portuguese ? "Não foi possível iniciar" : "Unable to launch"
                    self.showError(error.localizedDescription, title: errTitle)
                }
            }
        }
    }

    private func launch(game: GameManifest, runtime: URL, bios: URL, disc: SelectedDisc, gameData: URL) {
        do {
            let logs = fileManager.homeDirectoryForCurrentUser.appendingPathComponent("Library/Logs/ZeldaCDiNative", isDirectory: true)
            try fileManager.createDirectory(at: logs, withIntermediateDirectories: true, attributes: [.posixPermissions: 0o700])
            let formatter = DateFormatter()
            formatter.locale = Locale(identifier: "en_US_POSIX")
            formatter.dateFormat = "yyyy-MM-dd_HH-mm-ss"
            let log = logs.appendingPathComponent("\(game.id)-\(formatter.string(from: Date()))-\(UUID().uuidString.prefix(8)).log")
            guard fileManager.createFile(atPath: log.path, contents: nil, attributes: [.posixPermissions: 0o600]) else {
                let msg = L10n.currentLanguage == .portuguese ?
                    "Não foi possível criar o log de execução." : "Could not create execution log file."
                throw LauncherError.message(msg)
            }
            let handle = try FileHandle(forWritingTo: log)
            let header = "Zelda CD-i — \(game.title)\nStart: \(ISO8601DateFormatter().string(from: Date()))\n\n"
            try handle.write(contentsOf: Data(header.utf8))
            let child = Process()
            child.executableURL = runtime
            child.arguments = [bios.path, "--disc", disc.cue.path]
            child.currentDirectoryURL = gameData
            var environment = ProcessInfo.processInfo.environment
            environment["CDI_PLAYER_CONFIG_PATH"] = gameData.appendingPathComponent("player.cfg").path
            // The GUI language controls presentation for the next game process.
            // Always clear inherited overrides so English reliably preserves originals.
            environment.removeValue(forKey: "CDI_TEXT_MOD_PATH")
            environment.removeValue(forKey: "CDI_MENU_MOD_PATH")
            if L10n.currentLanguage == .portuguese, game.id == "adventure",
               let resources = Bundle.main.resourceURL {
                let bundledMod = resources.appendingPathComponent("adventure-ptbr.txt")
                if fileManager.fileExists(atPath: bundledMod.path) {
                    environment["CDI_TEXT_MOD_PATH"] = bundledMod.path
                    let menuMod = resources.appendingPathComponent("adventure-menu-ptbr.txt")
                    if fileManager.fileExists(atPath: menuMod.path) {
                        environment["CDI_MENU_MOD_PATH"] = menuMod.path
                    }
                }
            }
            child.environment = environment
            child.standardOutput = handle
            child.standardError = handle
            child.standardInput = FileHandle.nullDevice
            child.terminationHandler = { [weak self] finished in
                DispatchQueue.main.async { [weak self] in self?.runtimeFinished(finished, game: game) }
            }
            latestLog = log
            logHandle = handle
            process = child
            try child.run()
            busy = false
            status.stringValue = "\(game.title) \(L10n.t("status.running"))"
            updateControls()
            NSApp.deactivate()
        } catch {
            try? logHandle?.close()
            logHandle = nil
            process = nil
            busy = false
            status.stringValue = L10n.currentLanguage == .portuguese ?
                "O runtime não pôde ser aberto." : "Runtime could not be launched."
            updateControls()
            let errTitle = L10n.currentLanguage == .portuguese ? "Falha ao executar" : "Execution failure"
            showError(error.localizedDescription, title: errTitle)
        }
    }

    private func runtimeFinished(_ finished: Process, game: GameManifest) {
        guard process === finished else { return }
        let exit = finished.terminationStatus
        let wasSignal = finished.terminationReason == .uncaughtSignal
        let footer = "\nEnded: \(ISO8601DateFormatter().string(from: Date())) — \(wasSignal ? "signal" : "code") \(exit)\n"
        try? logHandle?.write(contentsOf: Data(footer.utf8))
        try? logHandle?.close()
        logHandle = nil
        process = nil
        busy = false
        status.stringValue = exit == 0 ? "\(game.title) \(L10n.t("status.exited_clean"))" :
            "\(game.title) \(L10n.t("status.exited_error"))"
        updateControls()
        if pendingTermination {
            NSApp.reply(toApplicationShouldTerminate: true)
            return
        }
        window.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
    }

    @objc private func stopGame() {
        guard let child = process, child.isRunning else { return }
        status.stringValue = L10n.t("status.stopping")
        stopButton.isEnabled = false
        child.terminate()
    }

    @objc private func openLog() {
        guard let url = latestLog else { return }
        NSWorkspace.shared.open(url)
    }

    @objc private func openSupport() {
        do {
            try fileManager.createDirectory(at: supportDirectory, withIntermediateDirectories: true,
                                             attributes: [.posixPermissions: 0o700])
            NSWorkspace.shared.open(supportDirectory)
        } catch {
            let errTitle = L10n.currentLanguage == .portuguese ? "Não foi possível abrir os dados" : "Unable to open data folder"
            showError(error.localizedDescription, title: errTitle)
        }
    }

    @objc private func showAbout() {
        let alert = NSAlert()
        alert.messageText = L10n.t("dialog.about_title")
        alert.informativeText = L10n.t("dialog.about_text")
        alert.addButton(withTitle: "OK")
        alert.beginSheetModal(for: window)
    }

    private func showError(_ message: String, title: String) {
        let alert = NSAlert()
        alert.alertStyle = .warning
        alert.messageText = title
        alert.informativeText = message
        alert.addButton(withTitle: "OK")
        alert.beginSheetModal(for: window)
    }

    func windowShouldClose(_ sender: NSWindow) -> Bool {
        NSApp.terminate(nil)
        return false
    }

    func applicationShouldTerminate(_ sender: NSApplication) -> NSApplication.TerminateReply {
        guard let child = process, child.isRunning else { return .terminateNow }
        let alert = NSAlert()
        alert.messageText = L10n.t("dialog.quit_title")
        alert.informativeText = L10n.t("dialog.quit_text")
        alert.addButton(withTitle: L10n.t("dialog.quit_confirm"))
        alert.addButton(withTitle: L10n.t("dialog.quit_cancel"))
        guard alert.runModal() == .alertFirstButtonReturn else { return .terminateCancel }
        pendingTermination = true
        stopGame()
        return .terminateLater
    }

    func applicationShouldHandleReopen(_ sender: NSApplication, hasVisibleWindows flag: Bool) -> Bool {
        window.makeKeyAndOrderFront(nil)
        return true
    }
}

// MARK: - Entrypoint

let application = NSApplication.shared
private let delegate = LauncherDelegate()
application.setActivationPolicy(.regular)
application.delegate = delegate
application.run()
