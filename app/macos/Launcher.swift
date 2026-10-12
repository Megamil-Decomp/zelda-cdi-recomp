import AppKit
import CryptoKit
import Foundation

// This launcher owns media selection and the child process. It does not emulate
// the CD-i, ship firmware, or claim that an experimental runtime is a full port.
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

private final class MediaValidator {
    private static let fileManager = FileManager.default

    static func regularFile(_ url: URL) throws -> Int64 {
        guard url.isFileURL else { throw LauncherError.message("Escolha um arquivo local.") }
        let values = try url.resourceValues(forKeys: [.isRegularFileKey, .fileSizeKey])
        guard values.isRegularFile == true, fileManager.isReadableFile(atPath: url.path) else {
            throw LauncherError.message("O arquivo não pode ser lido: \(url.lastPathComponent). Se ele foi movido, escolha novamente.")
        }
        return Int64(values.fileSize ?? 0)
    }

    // The runtime supports one contiguous, raw Mode-2 track. A selected BIN is
    // resolved through its companion CUE; the launcher never invents a layout.
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
                throw LauncherError.message("Este BIN precisa do arquivo CUE com o mesmo nome na mesma pasta. Escolha o CUE original do disco; a imagem não será copiada nem alterada.")
            }
            cue = companion
        }
        guard cue.pathExtension.lowercased() == "cue" else {
            throw LauncherError.message("Escolha uma imagem de disco .cue ou .bin com seu CUE correspondente.")
        }
        let cueSize = try regularFile(cue)
        guard cueSize > 0 && cueSize <= 65_536 else {
            throw LauncherError.message("O descritor CUE está vazio ou é grande demais para este formato.")
        }
        let bytes = try Data(contentsOf: cue)
        guard let source = String(data: bytes, encoding: .utf8) ?? String(data: bytes, encoding: .isoLatin1) else {
            throw LauncherError.message("Não foi possível ler o texto do arquivo CUE.")
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
            throw LauncherError.message("Este runtime aceita um CUE com uma única faixa CDI/2352 ou MODE2/2352, iniciando em INDEX 01 00:00:00, sem pregap. Selecione o descritor original compatível.")
        }
        let name = capture(#"^FILE\s+"([^"]+)"\s+BINARY\s*$"#, files[0]) ??
            capture(#"^FILE\s+(\S+)\s+BINARY\s*$"#, files[0])
        guard let filename = name, !filename.isEmpty,
              !filename.contains("/"), !filename.contains("\\"),
              filename != ".", filename != ".." else {
            throw LauncherError.message("O CUE deve apontar para um único arquivo BIN na mesma pasta. Mantenha os dois arquivos juntos com os nomes originais.")
        }
        let bin = cue.deletingLastPathComponent().appendingPathComponent(filename)
        let binSize = try regularFile(bin)
        guard binSize > 0, binSize % 2352 == 0 else {
            throw LauncherError.message("O BIN não contém uma quantidade inteira de setores de 2352 bytes ou está vazio.")
        }
        if selectedURL.pathExtension.lowercased() == "bin",
           selectedURL.resolvingSymlinksInPath().standardizedFileURL != bin.resolvingSymlinksInPath().standardizedFileURL {
            throw LauncherError.message("O CUE encontrado aponta para outro BIN. Escolha diretamente o CUE correto.")
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
            throw LauncherError.message("O arquivo mudou durante a verificação. Aguarde a cópia terminar e tente novamente.")
        }
        progress(1)
        return hasher.finalize().map { String(format: "%02x", $0) }.joined()
    }

    static func bios(at selectedURL: URL, manifest: BIOSManifest, support: URL) throws -> URL {
        guard try regularFile(selectedURL) == manifest.size else {
            throw LauncherError.message("Esta BIOS precisa ter exatamente \(manifest.size) bytes. Escolha a BIOS compatível com esta compilação.")
        }
        let digest = try sha256(selectedURL, progress: { _ in })
        let runtimeDigest = (manifest.runtimeSHA256 ?? manifest.sha256).lowercased()
        if digest == runtimeDigest { return selectedURL }
        guard digest == manifest.sha256.lowercased() else {
            throw LauncherError.message("A BIOS selecionada pertence a outra revisão. Este aplicativo contém código recompilado para uma BIOS específica; escolha a BIOS usada para gerar esta compilação.")
        }
        guard manifest.byteOrder == "swap16", manifest.size % 2 == 0 else {
            throw LauncherError.message("A ordem de bytes desta BIOS não é compatível com o runtime incluído.")
        }
        var firmware = try Data(contentsOf: selectedURL)
        guard firmware.count == Int(manifest.size) else {
            throw LauncherError.message("A BIOS mudou durante a leitura. Escolha novamente o arquivo original.")
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
            throw LauncherError.message("A conversão da BIOS não corresponde à identidade exigida pelo runtime. A mídia original foi preservada.")
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
    private let biosPath = NSTextField(labelWithString: "Nenhuma BIOS selecionada")
    private let discPath = NSTextField(labelWithString: "Nenhum disco selecionado")
    private let status = NSTextField(wrappingLabelWithString: "Escolha um jogo e informe sua mídia.")
    private let progress = NSProgressIndicator()
    private var biosButton: NSButton!
    private var discButton: NSButton!
    private var playButton: NSButton!
    private var stopButton: NSButton!
    private var logButton: NSButton!
    private var busy = false
    private var process: Process?
    private var logHandle: FileHandle?
    private var latestLog: URL?
    private var pendingTermination = false
    private var selectedIndex = 0

    private var selectedGame: GameManifest? {
        guard let games = manifest?.games, games.indices.contains(selectedIndex) else { return nil }
        return games[selectedIndex]
    }

    private var supportDirectory: URL {
        fileManager.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0]
            .appendingPathComponent("ZeldaCDiNative", isDirectory: true)
    }

    func applicationDidFinishLaunching(_ notification: Notification) {
        loadManifest()
        buildMenu()
        buildWindow()
        autodetectLocalMedia()
        if let games = manifest?.games, !games.isEmpty {
            let previous = defaults.string(forKey: "selectedGame")
            selectedIndex = games.firstIndex(where: { $0.id == previous }) ?? 0
            table.selectRowIndexes(IndexSet(integer: selectedIndex), byExtendingSelection: false)
        }
        refreshSelection()
        window.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
        if let failure = manifestFailure {
            status.stringValue = "Aplicativo incompleto. Consulte a mensagem de instalação."
            showError(failure, title: "Não foi possível carregar o aplicativo")
        }
    }

    private func loadManifest() {
        do {
            guard let url = Bundle.main.url(forResource: "runtime-manifest", withExtension: "json") else {
                throw LauncherError.message("O manifesto dos runtimes não está no aplicativo. Gere novamente o pacote .app completo.")
            }
            let decoded = try JSONDecoder().decode(RuntimeManifest.self, from: Data(contentsOf: url))
            guard decoded.schemaVersion == 1, !decoded.games.isEmpty,
                  decoded.bios.size > 0, validDigest(decoded.bios.sha256),
                  decoded.bios.runtimeSHA256.map(validDigest) ?? true,
                  decoded.bios.byteOrder == nil || decoded.bios.byteOrder == "swap16",
                  Set(decoded.games.map(\.id)).count == decoded.games.count else {
                throw LauncherError.message("O manifesto do aplicativo tem uma versão ou identidade de mídia inválida.")
            }
            for game in decoded.games {
                guard game.id.range(of: #"^[a-z0-9_-]+$"#, options: .regularExpression) != nil,
                      game.runtime.range(of: #"^[A-Za-z0-9][A-Za-z0-9._-]*$"#, options: .regularExpression) != nil,
                      validDigest(game.discSHA256), !game.title.isEmpty else {
                    throw LauncherError.message("O manifesto contém um caminho ou jogo inválido.")
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
        appMenu.addItem(withTitle: "Sobre Zelda CD-i", action: #selector(showAbout), keyEquivalent: "")
        appMenu.addItem(NSMenuItem.separator())
        appMenu.addItem(withTitle: "Ocultar Zelda CD-i", action: #selector(NSApplication.hide(_:)), keyEquivalent: "h")
        appMenu.addItem(withTitle: "Sair do Zelda CD-i", action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q")
        let fileRoot = NSMenuItem(title: "Arquivo", action: nil, keyEquivalent: "")
        let fileMenu = NSMenu(title: "Arquivo")
        fileMenu.addItem(withTitle: "Escolher disco…", action: #selector(chooseDisc), keyEquivalent: "o")
        fileMenu.addItem(withTitle: "Abrir último log", action: #selector(openLog), keyEquivalent: "l")
        fileMenu.addItem(withTitle: "Abrir pasta de dados", action: #selector(openSupport), keyEquivalent: "")
        fileRoot.submenu = fileMenu
        menu.addItem(fileRoot)
        NSApp.mainMenu = menu
    }

    private func buildWindow() {
        window = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 900, height: 560),
                          styleMask: [.titled, .closable, .miniaturizable, .resizable],
                          backing: .buffered, defer: false)
        window.title = "Zelda CD-i"
        window.minSize = NSSize(width: 790, height: 510)
        window.center()
        window.delegate = self
        window.isReleasedWhenClosed = false

        let root = NSStackView()
        root.orientation = .vertical
        root.alignment = .leading
        root.spacing = 20
        root.translatesAutoresizingMaskIntoConstraints = false
        window.contentView!.addSubview(root)
        NSLayoutConstraint.activate([
            root.leadingAnchor.constraint(equalTo: window.contentView!.leadingAnchor, constant: 26),
            root.trailingAnchor.constraint(equalTo: window.contentView!.trailingAnchor, constant: -26),
            root.topAnchor.constraint(equalTo: window.contentView!.topAnchor, constant: 26),
            root.bottomAnchor.constraint(equalTo: window.contentView!.bottomAnchor, constant: -24)
        ])

        let header = NSStackView()
        header.orientation = .vertical
        header.alignment = .leading
        header.spacing = 5
        let title = NSTextField(labelWithString: "Zelda CD-i")
        title.font = .systemFont(ofSize: 29, weight: .bold)
        header.addArrangedSubview(title)
        let subtitle = NSTextField(labelWithString: "Biblioteca local · macOS arm64 · versão experimental")
        subtitle.textColor = .secondaryLabelColor
        subtitle.font = .systemFont(ofSize: 13)
        header.addArrangedSubview(subtitle)
        root.addArrangedSubview(header)

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
        let libraryLabel = NSTextField(labelWithString: "SEUS JOGOS")
        libraryLabel.font = .systemFont(ofSize: 11, weight: .semibold)
        libraryLabel.textColor = .secondaryLabelColor
        library.addArrangedSubview(libraryLabel)
        let scroll = NSScrollView()
        scroll.hasVerticalScroller = true
        scroll.borderType = .lineBorder
        table = NSTableView()
        let column = NSTableColumn(identifier: NSUserInterfaceItemIdentifier("game"))
        column.width = 245
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
        scroll.widthAnchor.constraint(equalToConstant: 252).isActive = true
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
        detail.addArrangedSubview(makeMediaRow(title: "BIOS CD-i", path: biosPath, selector: #selector(chooseBIOS), isBIOS: true))
        detail.addArrangedSubview(makeMediaRow(title: "Disco do jogo", path: discPath, selector: #selector(chooseDisc), isBIOS: false))

        let controls = NSStackView()
        controls.orientation = .horizontal
        controls.spacing = 10
        playButton = NSButton(title: "Iniciar jogo", target: self, action: #selector(startGame))
        playButton.bezelStyle = .rounded
        playButton.keyEquivalent = "\r"
        stopButton = NSButton(title: "Parar", target: self, action: #selector(stopGame))
        stopButton.bezelStyle = .rounded
        controls.addArrangedSubview(playButton)
        controls.addArrangedSubview(stopButton)
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
        logButton = NSButton(title: "Abrir log", target: self, action: #selector(openLog))
        logButton.bezelStyle = .rounded
        footer.addArrangedSubview(logButton)
        root.addArrangedSubview(footer)
        footer.widthAnchor.constraint(equalTo: root.widthAnchor).isActive = true
        let note = NSTextField(wrappingLabelWithString: "Use seus arquivos originais. O aplicativo não copia os discos e verifica a revisão antes de iniciar.")
        note.font = .systemFont(ofSize: 11)
        note.textColor = .secondaryLabelColor
        root.addArrangedSubview(note)
        note.widthAnchor.constraint(equalTo: root.widthAnchor).isActive = true
    }

    private func makeMediaRow(title: String, path: NSTextField, selector: Selector, isBIOS: Bool) -> NSView {
        let group = NSStackView()
        group.orientation = .vertical
        group.alignment = .leading
        group.spacing = 6
        let label = NSTextField(labelWithString: title)
        label.font = .systemFont(ofSize: 12, weight: .semibold)
        group.addArrangedSubview(label)
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
        let button = NSButton(title: "Escolher…", target: self, action: selector)
        button.bezelStyle = .rounded
        row.addArrangedSubview(button)
        if isBIOS { biosButton = button } else { discButton = button }
        group.addArrangedSubview(row)
        row.widthAnchor.constraint(equalTo: group.widthAnchor).isActive = true
        return group
    }

    private func autodetectLocalMedia() {
        guard let manifest = manifest, let rootPath = manifest.localMediaRoot else { return }
        let root = URL(fileURLWithPath: rootPath, isDirectory: true).standardizedFileURL
        func existingLocal(_ relative: String?) -> String? {
            guard let relative = relative, !relative.hasPrefix("/") else { return nil }
            let url = root.appendingPathComponent(relative).standardizedFileURL
            guard url.path.hasPrefix(root.path + "/"), fileManager.isReadableFile(atPath: url.path) else { return nil }
            return url.path
        }
        if defaults.string(forKey: "biosPath") == nil, let path = existingLocal(manifest.bios.localRelative) {
            defaults.set(path, forKey: "biosPath")
        }
        for game in manifest.games where defaults.string(forKey: discKey(game)) == nil {
            if let path = existingLocal(game.localCueRelative) { defaults.set(path, forKey: discKey(game)) }
        }
    }

    private func discKey(_ game: GameManifest) -> String { "discPath.\(game.id)" }

    private func refreshSelection() {
        guard let game = selectedGame else {
            gameStatus.stringValue = "Nenhum runtime disponível nesta instalação."
            updateControls()
            return
        }
        defaults.set(game.id, forKey: "selectedGame")
        gameTitle.stringValue = game.title
        gameStatus.stringValue = "\(game.statusText). Compatibilidade em validação; a presença na lista não comprova que o jogo esteja jogável."
        let bios = defaults.string(forKey: "biosPath")
        let disc = defaults.string(forKey: discKey(game))
        biosPath.stringValue = bios ?? "Selecione a BIOS desta compilação"
        biosPath.toolTip = bios
        discPath.stringValue = disc ?? "Selecione o CUE ou o BIN correspondente"
        discPath.toolTip = disc
        if !busy && process == nil {
            status.stringValue = "\(game.title) selecionado. Os arquivos serão verificados ao iniciar."
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
        let state = NSTextField(labelWithString: game.statusText)
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
        panel.title = "Escolher BIOS CD-i"
        panel.message = "Selecione a BIOS usada para gerar esta compilação. O arquivo original será preservado."
        panel.allowedFileTypes = ["rom", "bin"]
        panel.canChooseDirectories = false
        panel.allowsMultipleSelection = false
        if let path = defaults.string(forKey: "biosPath") { panel.directoryURL = URL(fileURLWithPath: path).deletingLastPathComponent() }
        panel.beginSheetModal(for: window) { [weak self] result in
            guard let self = self, result == .OK, let url = panel.url else { return }
            self.defaults.set(url.path, forKey: "biosPath")
            self.refreshSelection()
        }
    }

    @objc private func chooseDisc() {
        guard !busy && process == nil, let game = selectedGame else { return }
        let panel = NSOpenPanel()
        panel.title = "Escolher disco — \(game.title)"
        panel.message = "CUE e BIN devem permanecer juntos na mesma pasta. Nenhum disco será copiado para o aplicativo."
        panel.allowedFileTypes = ["cue", "bin"]
        panel.canChooseDirectories = false
        panel.allowsMultipleSelection = false
        if let path = defaults.string(forKey: discKey(game)) { panel.directoryURL = URL(fileURLWithPath: path).deletingLastPathComponent() }
        panel.beginSheetModal(for: window) { [weak self] result in
            guard let self = self, result == .OK, let url = panel.url else { return }
            do {
                let disc = try MediaValidator.disc(at: url)
                self.defaults.set(disc.cue.path, forKey: self.discKey(game))
                self.refreshSelection()
            } catch { self.showError(error.localizedDescription, title: "Disco incompatível") }
        }
    }

    @objc private func startGame() {
        guard !busy, process == nil, let manifest = manifest, let game = selectedGame,
              let bios = defaults.string(forKey: "biosPath"),
              let disc = defaults.string(forKey: discKey(game)) else { return }
        let runtime = Bundle.main.bundleURL.appendingPathComponent("Contents/MacOS").appendingPathComponent(game.runtime)
        guard fileManager.isExecutableFile(atPath: runtime.path) else {
            showError("O runtime de \(game.title) não está incluído ou não pode ser executado. Gere novamente o pacote completo.", title: "Runtime indisponível")
            return
        }
        busy = true
        status.stringValue = "Verificando BIOS…"
        updateControls()
        let support = supportDirectory
        worker.async { [weak self] in
            guard let self = self else { return }
            do {
                let biosURL = try MediaValidator.bios(at: URL(fileURLWithPath: bios), manifest: manifest.bios, support: support)
                let selectedDisc = try MediaValidator.disc(at: URL(fileURLWithPath: disc))
                let digest = try MediaValidator.sha256(selectedDisc.bin) { fraction in
                    DispatchQueue.main.async { [weak self] in
                        self?.status.stringValue = "Verificando disco de \(game.title)… \(Int(fraction * 100))%"
                    }
                }
                guard digest == game.discSHA256.lowercased() else {
                    throw LauncherError.message("O disco não corresponde à revisão recompilada de \(game.title). Escolha o BIN/CUE usado para gerar este aplicativo. Outras edições exigem outra compilação.")
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
                    self.status.stringValue = "A mídia não passou na verificação."
                    self.updateControls()
                    self.showError(error.localizedDescription, title: "Não foi possível iniciar")
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
                throw LauncherError.message("Não foi possível criar o log de execução.")
            }
            let handle = try FileHandle(forWritingTo: log)
            let header = "Zelda CD-i — \(game.title)\nVersão experimental; gameplay ainda em validação.\nInício: \(ISO8601DateFormatter().string(from: Date()))\n\n"
            try handle.write(contentsOf: Data(header.utf8))
            let child = Process()
            child.executableURL = runtime
            child.arguments = [bios.path, "--disc", disc.cue.path]
            child.currentDirectoryURL = gameData
            var environment = ProcessInfo.processInfo.environment
            environment["CDI_PLAYER_CONFIG_PATH"] = gameData.appendingPathComponent("player.cfg").path
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
            status.stringValue = "\(game.title) em execução. Use a janela do jogo; o log registra a sessão."
            updateControls()
            NSApp.deactivate()
        } catch {
            try? logHandle?.close()
            logHandle = nil
            process = nil
            busy = false
            status.stringValue = "O runtime não pôde ser aberto."
            updateControls()
            showError(error.localizedDescription, title: "Falha ao executar")
        }
    }

    private func runtimeFinished(_ finished: Process, game: GameManifest) {
        guard process === finished else { return }
        let exit = finished.terminationStatus
        let wasSignal = finished.terminationReason == .uncaughtSignal
        let footer = "\nEncerrado: \(ISO8601DateFormatter().string(from: Date())) — \(wasSignal ? "sinal" : "código") \(exit)\n"
        try? logHandle?.write(contentsOf: Data(footer.utf8))
        try? logHandle?.close()
        logHandle = nil
        process = nil
        busy = false
        status.stringValue = exit == 0 ? "\(game.title) encerrado. Consulte o log para detalhes da sessão." :
            "\(game.title) encerrou com \(wasSignal ? "sinal" : "código") \(exit). Abra o log para investigar."
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
        status.stringValue = "Encerrando o runtime…"
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
        } catch { showError(error.localizedDescription, title: "Não foi possível abrir os dados") }
    }

    @objc private func showAbout() {
        let alert = NSAlert()
        alert.messageText = "Zelda CD-i · versão experimental"
        alert.informativeText = "Launcher local para os runtimes incluídos nesta compilação. A compatibilidade dos jogos está em validação. A execução pode incluir fallback interpretado e não comprova recompilação estática completa.\n\nForneça suas próprias imagens de disco e BIOS. Textos e áudio originais são preservados."
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
        alert.messageText = "Encerrar o jogo e sair?"
        alert.informativeText = "O runtime de jogo ainda está em execução. Ao sair, ele receberá uma solicitação para encerrar."
        alert.addButton(withTitle: "Encerrar e sair")
        alert.addButton(withTitle: "Continuar jogando")
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

let application = NSApplication.shared
let delegate = LauncherDelegate()
application.setActivationPolicy(.regular)
application.delegate = delegate
application.run()
