/* Author-written Win32 launcher. Package metadata is generated privately. */
#ifndef UNICODE
#define UNICODE
#endif
#ifndef _UNICODE
#define _UNICODE
#endif
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <shellapi.h>
#include <shlobj.h>
#include <bcrypt.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <wchar.h>

typedef struct {
    const wchar_t *id, *title, *runtime, *cue, *image;
    const char *runtime_hash, *disc_hash, *cue_hash;
} Game;
#include "package_config.h"

#define CAP 32768
#define ID_GAMES 101
#define ID_PLAY 102
#define ID_STOP 103
#define ID_LOG 104
#define ID_MOD 105
#define ID_DATA 106
#define WM_FINISHED (WM_APP + 1)
static HWND window, list, play, stop, status, log_button, mod_button, data_button;
static HFONT font;
static wchar_t base[CAP], support[CAP], log_path[CAP], error_text[1024];
static PROCESS_INFORMATION child;
static int busy, closing, selected, use_mod;

static int join(wchar_t *out, const wchar_t *root, const wchar_t *relative) {
    return swprintf(out, CAP, L"%ls\\%ls", root, relative) > 0;
}

static int readable(const wchar_t *path) {
    DWORD a = GetFileAttributesW(path);
    return a != INVALID_FILE_ATTRIBUTES && !(a & FILE_ATTRIBUTE_DIRECTORY);
}

static int directory(const wchar_t *path) {
    int result = SHCreateDirectoryExW(NULL, path, NULL);
    return result == ERROR_SUCCESS || result == ERROR_ALREADY_EXISTS || result == ERROR_FILE_EXISTS;
}

static int file_hash(const wchar_t *path, const char *expected) {
    FILE *f = _wfopen(path, L"rb");
    if (!f) return 0;
    BCRYPT_ALG_HANDLE algorithm = NULL;
    BCRYPT_HASH_HANDLE context = NULL;
    uint8_t hash[32], *block = malloc(1024 * 1024);
    char hex[65];
    if (!block) { fclose(f); return 0; }
    if (BCryptOpenAlgorithmProvider(&algorithm, BCRYPT_SHA256_ALGORITHM, NULL, 0) < 0 ||
        BCryptCreateHash(algorithm, &context, NULL, 0, NULL, 0, 0) < 0) {
        if (algorithm) BCryptCloseAlgorithmProvider(algorithm, 0);
        free(block); fclose(f); return 0;
    }
    size_t size;
    int ok = 1;
    while ((size = fread(block, 1, 1024 * 1024, f)) != 0) {
        if (BCryptHashData(context, block, (ULONG)size, 0) < 0) { ok = 0; break; }
    }
    ok = ok && !ferror(f);
    fclose(f); free(block);
    if (BCryptFinishHash(context, hash, sizeof(hash), 0) < 0) ok = 0;
    BCryptDestroyHash(context); BCryptCloseAlgorithmProvider(algorithm, 0);
    if (!ok) return 0;
    for (int i = 0; i < 32; i++) sprintf(hex + 2 * i, "%02x", hash[i]);
    return ok && strcmp(hex, expected) == 0;
}

static int normalized_bios(wchar_t *out) {
    wchar_t source[CAP], temp[CAP];
    join(source, base, BIOS_RELATIVE);
    if (!file_hash(source, BIOS_HASH)) return 0;
    join(out, support, L"bios-normalizada.rom");
    if (file_hash(out, BIOS_RUNTIME_HASH)) return 1;
    FILE *f = _wfopen(source, L"rb");
    if (!f) return 0;
    uint8_t *bytes = malloc(BIOS_SIZE);
    if (!bytes) { fclose(f); return 0; }
    int ok = fread(bytes, 1, BIOS_SIZE, f) == BIOS_SIZE && fgetc(f) == EOF;
    fclose(f);
    if (ok && BIOS_SWAP16) for (size_t i = 0; i < BIOS_SIZE; i += 2) {
        uint8_t t = bytes[i]; bytes[i] = bytes[i + 1]; bytes[i + 1] = t;
    }
    join(temp, support, L"bios-normalizada.tmp");
    if (ok) {
        f = _wfopen(temp, L"wb");
        if (!f) ok = 0;
        else { ok = fwrite(bytes, 1, BIOS_SIZE, f) == BIOS_SIZE; if (fclose(f)) ok = 0; }
    }
    free(bytes);
    if (ok) ok = file_hash(temp, BIOS_RUNTIME_HASH) && MoveFileExW(temp, out, MOVEFILE_REPLACE_EXISTING);
    if (!ok) DeleteFileW(temp);
    return ok;
}

static void error(const wchar_t *message) {
    wcsncpy(error_text, message, 1023); error_text[1023] = 0;
}

static DWORD WINAPI start_worker(void *unused) {
    (void)unused;
    wchar_t executable[CAP], cue[CAP], image[CAP], bios[CAP], data[CAP], config[CAP], mod[CAP];
    const Game *g = &games[selected];
    join(executable, base, g->runtime); join(cue, base, g->cue); join(image, base, g->image);
    join(data, support, g->id);
    error_text[0] = 0;
    if (!directory(support) || !directory(data)) { error(L"Não foi possível criar a pasta de saves."); goto done; }
    if (!file_hash(executable, g->runtime_hash)) { error(L"O runtime está ausente ou foi alterado. Extraia novamente o ZIP completo."); goto done; }
    if (!file_hash(cue, g->cue_hash) || !file_hash(image, g->disc_hash)) { error(L"Disco ausente ou checksum incompatível. Mantenha a pasta completa extraída."); goto done; }
    if (!normalized_bios(bios)) { error(L"Não foi possível validar ou preparar a BIOS."); goto done; }
    join(config, data, L"player.cfg");
    if (!readable(config)) {
        FILE *f = _wfopen(config, L"wb");
        if (!f) { error(L"Não foi possível salvar a configuração."); goto done; }
        fputs("[input]\ncapture_mouse = false\n", f); fclose(f);
    }
    SetEnvironmentVariableW(L"CDI_PLAYER_CONFIG_PATH", config);
    SetEnvironmentVariableW(L"CDI_UI_LANGUAGE", L"pt-BR");
    SetEnvironmentVariableW(L"CDI_TEXT_MOD_PATH", NULL);
    SetEnvironmentVariableW(L"CDI_MENU_MOD_PATH", NULL);
    if (use_mod && wcscmp(g->id, L"adventure") == 0) {
        join(mod, base, L"mods\\adventure-ptbr.txt"); SetEnvironmentVariableW(L"CDI_TEXT_MOD_PATH", mod);
        join(mod, base, L"mods\\adventure-menu-ptbr.txt"); SetEnvironmentVariableW(L"CDI_MENU_MOD_PATH", mod);
    }
    SYSTEMTIME now; GetLocalTime(&now);
    swprintf(log_path, CAP, L"%ls\\%ls\\sessao-%04u%02u%02u-%02u%02u%02u-%lu.log", support, g->id,
             now.wYear, now.wMonth, now.wDay, now.wHour, now.wMinute, now.wSecond, GetCurrentProcessId());
    SECURITY_ATTRIBUTES sa = {sizeof(sa), NULL, TRUE};
    HANDLE log = CreateFileW(log_path, GENERIC_WRITE, FILE_SHARE_READ, &sa, CREATE_NEW, FILE_ATTRIBUTE_NORMAL, NULL);
    if (log == INVALID_HANDLE_VALUE) { error(L"Não foi possível criar o log."); goto done; }
    char heading[] = "Zelda CD-i: Windows x64 experimental\r\n"; DWORD written;
    WriteFile(log, heading, sizeof(heading) - 1, &written, NULL);
    /* Paths are quoted as complete argv elements; filenames cannot contain a quote. */
    wchar_t *command = malloc(CAP * sizeof(wchar_t));
    if (!command || swprintf(command, CAP, L"\"%ls\" \"%ls\" --disc \"%ls\"", executable, bios, cue) < 0) {
        free(command); CloseHandle(log); error(L"Caminho longo demais para iniciar o jogo."); goto done;
    }
    STARTUPINFOW startup = {0}; startup.cb = sizeof(startup);
    startup.dwFlags = STARTF_USESTDHANDLES;
    startup.hStdOutput = log; startup.hStdError = log;
    startup.hStdInput = CreateFileW(L"NUL", GENERIC_READ, FILE_SHARE_READ | FILE_SHARE_WRITE, &sa, OPEN_EXISTING, 0, NULL);
    BOOL launched = CreateProcessW(executable, command, NULL, NULL, TRUE, CREATE_NO_WINDOW, NULL, data, &startup, &child);
    DWORD launch_error = GetLastError();
    if (startup.hStdInput != INVALID_HANDLE_VALUE) CloseHandle(startup.hStdInput);
    free(command); CloseHandle(log);
    if (!launched) swprintf(error_text, 1024, L"Falha ao iniciar (Windows %lu). Consulte o log e confira as DLLs do pacote.", launch_error);
done:
    PostMessageW(window, WM_FINISHED, 0, 0);
    return 0;
}

static BOOL CALLBACK close_child_window(HWND hwnd, LPARAM pid) {
    DWORD owner = 0; GetWindowThreadProcessId(hwnd, &owner);
    if (owner == (DWORD)pid) PostMessageW(hwnd, WM_CLOSE, 0, 0);
    return TRUE;
}

static void controls(void) {
    int running = child.hProcess != NULL;
    EnableWindow(play, !busy && !running);
    EnableWindow(list, !busy && !running);
    EnableWindow(mod_button, !busy && !running);
    EnableWindow(stop, running);
    EnableWindow(log_button, log_path[0] != 0);
}

static HWND control(const wchar_t *class_name, const wchar_t *text, DWORD style,
                    int x, int y, int width, int height, int id) {
    if (wcscmp(class_name, L"BUTTON") == 0 || wcscmp(class_name, L"LISTBOX") == 0) style |= WS_TABSTOP;
    HWND h = CreateWindowW(class_name, text, WS_CHILD | WS_VISIBLE | style,
                          x, y, width, height, window, (HMENU)(INT_PTR)id, NULL, NULL);
    SendMessageW(h, WM_SETFONT, (WPARAM)font, TRUE);
    return h;
}

static LRESULT CALLBACK wndproc(HWND hwnd, UINT message, WPARAM w, LPARAM l) {
    switch (message) {
    case WM_CREATE:
        window = hwnd;
        font = CreateFontW(-17, 0, 0, 0, FW_NORMAL, FALSE, FALSE, FALSE, DEFAULT_CHARSET,
                           OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS, CLEARTYPE_QUALITY, DEFAULT_PITCH, L"Segoe UI");
        control(L"STATIC", L"Zelda CD-i — Windows x64", 0, 24, 20, 650, 28, 0);
        control(L"STATIC", L"Versão experimental · mídia local incluída · selecione um jogo", 0, 24, 58, 680, 24, 0);
        list = control(L"LISTBOX", L"", WS_BORDER | LBS_NOTIFY, 24, 96, 680, 95, ID_GAMES);
        for (int i = 0; i < 3; i++) SendMessageW(list, LB_ADDSTRING, 0, (LPARAM)games[i].title);
        SendMessageW(list, LB_SETCURSEL, 0, 0);
        mod_button = control(L"BUTTON", L"PT-BR parcial de Adventure (slots e botões do menu)", BS_AUTOCHECKBOX,
                             24, 208, 680, 28, ID_MOD);
        play = control(L"BUTTON", L"Iniciar jogo", BS_DEFPUSHBUTTON, 24, 254, 150, 36, ID_PLAY);
        stop = control(L"BUTTON", L"Parar", BS_PUSHBUTTON, 188, 254, 110, 36, ID_STOP);
        log_button = control(L"BUTTON", L"Abrir log", BS_PUSHBUTTON, 312, 254, 145, 36, ID_LOG);
        data_button = control(L"BUTTON", L"Saves e logs", BS_PUSHBUTTON, 470, 254, 180, 36, ID_DATA);
        status = control(L"STATIC", L"Pronto. Os arquivos serão verificados ao iniciar.", 0, 24, 312, 680, 48, 0);
        control(L"STATIC", L"Controles: setas/WASD · ação: Espaço/Enter/Z · secundário: X/Backspace\nFeche a janela do jogo para salvar. Campanha completa ainda em validação.",
                0, 24, 370, 680, 54, 0);
        controls(); SetTimer(hwnd, 1, 500, NULL); return 0;
    case WM_COMMAND:
        switch (LOWORD(w)) {
        case ID_PLAY: {
            if (busy || child.hProcess) break;
            selected = (int)SendMessageW(list, LB_GETCURSEL, 0, 0);
            if (selected < 0 || selected > 2) break;
            use_mod = SendMessageW(mod_button, BM_GETCHECK, 0, 0) == BST_CHECKED;
            busy = 1; SetWindowTextW(status, L"Verificando os arquivos… aguarde."); controls();
            HANDLE worker = CreateThread(NULL, 0, start_worker, NULL, 0, NULL);
            if (worker) CloseHandle(worker);
            else { busy = 0; SetWindowTextW(status, L"Não foi possível iniciar a verificação."); controls(); }
            break;
        }
        case ID_STOP: if (child.hProcess) {
            EnumWindows(close_child_window, child.dwProcessId);
            SetWindowTextW(status, L"Aguardando o jogo fechar e salvar…");
        } break;
        case ID_LOG: if (log_path[0]) ShellExecuteW(hwnd, L"open", log_path, NULL, NULL, SW_SHOWNORMAL); break;
        case ID_DATA: directory(support); ShellExecuteW(hwnd, L"open", support, NULL, NULL, SW_SHOWNORMAL); break;
        } return 0;
    case WM_FINISHED:
        busy = 0;
        if (error_text[0]) { SetWindowTextW(status, L"Falha ao iniciar."); MessageBoxW(hwnd, error_text, L"Zelda CD-i", MB_OK | MB_ICONERROR); }
        else SetWindowTextW(status, L"Jogo em execução. Feche a janela do jogo para salvar.");
        controls(); return 0;
    case WM_TIMER:
        if (!busy && child.hProcess && WaitForSingleObject(child.hProcess, 0) == WAIT_OBJECT_0) {
            DWORD code; GetExitCodeProcess(child.hProcess, &code);
            CloseHandle(child.hProcess); CloseHandle(child.hThread); memset(&child, 0, sizeof(child));
            wchar_t text[256]; swprintf(text, 256, L"Jogo encerrado (código 0x%08lX). Log disponível para diagnóstico.", code);
            SetWindowTextW(status, text); controls();
            if (closing) DestroyWindow(hwnd);
        } return 0;
    case WM_CLOSE:
        if (busy) { MessageBoxW(hwnd, L"Aguarde a verificação dos arquivos terminar.", L"Zelda CD-i", MB_OK); return 0; }
        if (child.hProcess) {
            if (MessageBoxW(hwnd, L"Fechar o jogo e a interface?", L"Zelda CD-i", MB_YESNO | MB_ICONQUESTION) != IDYES) return 0;
            closing = 1; EnumWindows(close_child_window, child.dwProcessId);
            SetWindowTextW(status, L"Aguardando o jogo fechar e salvar…"); return 0;
        }
        DestroyWindow(hwnd); return 0;
    case WM_DESTROY: if (font) DeleteObject(font); PostQuitMessage(0); return 0;
    }
    return DefWindowProcW(hwnd, message, w, l);
}

int WINAPI wWinMain(HINSTANCE instance, HINSTANCE previous, wchar_t *args, int show) {
    (void)previous; (void)args;
    HANDLE singleton = CreateMutexW(NULL, FALSE, L"Local\\ZeldaCDiNativeWindowsLauncher");
    if (!singleton) return 1;
    if (GetLastError() == ERROR_ALREADY_EXISTS) {
        HWND existing = FindWindowW(L"ZeldaCDiPortableWindow", NULL);
        if (existing) { ShowWindow(existing, SW_RESTORE); SetForegroundWindow(existing); }
        CloseHandle(singleton); return 0;
    }
    if (!GetModuleFileNameW(NULL, base, CAP) || !wcsrchr(base, L'\\')) return 1;
    *wcsrchr(base, L'\\') = 0;
    wchar_t local[MAX_PATH];
    if (FAILED(SHGetFolderPathW(NULL, CSIDL_LOCAL_APPDATA, NULL, SHGFP_TYPE_CURRENT, local))) return 1;
    join(support, local, L"ZeldaCDiNative");
    WNDCLASSW wc = {0}; wc.lpfnWndProc = wndproc; wc.hInstance = instance;
    wc.hCursor = LoadCursorW(NULL, IDC_ARROW); wc.hbrBackground = (HBRUSH)(COLOR_WINDOW + 1);
    wc.lpszClassName = L"ZeldaCDiPortableWindow";
    if (!RegisterClassW(&wc)) return 1;
    HWND h = CreateWindowW(wc.lpszClassName, L"Zelda CD-i — Windows experimental", WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU | WS_MINIMIZEBOX,
                           CW_USEDEFAULT, CW_USEDEFAULT, 750, 490, NULL, NULL, instance, NULL);
    if (!h) return 1;
    ShowWindow(h, show); UpdateWindow(h);
    MSG message;
    while (GetMessageW(&message, NULL, 0, 0) > 0) {
        if (!IsDialogMessageW(h, &message)) { TranslateMessage(&message); DispatchMessageW(&message); }
    }
    CloseHandle(singleton); return 0;
}
