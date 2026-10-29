#pragma once
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

/* Original adapter: one confirmed ASCII label, read only during rendering.
 * This pilot does not modify guest RAM or implement general localization. */
typedef struct { int loaded, enabled; char label[6]; uint64_t hits; } CdiTextMod;

static int cdi_text_mod_load(CdiTextMod *mod, const char *path) {
    memset(mod, 0, sizeof *mod);
    mod->loaded = 1;
    if (!path || !*path) return 1;
    FILE *file = fopen(path, "r");
    if (!file) return 0;
    char line[256];
    int enabled_seen = 0, label_seen = 0, valid = 1;
    while (fgets(line, sizeof line, file)) {
        size_t length = strlen(line);
        if (length == sizeof line - 1 && line[length - 1] != '\n') { valid = 0; break; }
        while (length && (line[length - 1] == '\n' || line[length - 1] == '\r')) line[--length] = 0;
        if (!length || line[0] == '#') continue;
        if (!strcmp(line, "enabled=true") || !strcmp(line, "enabled=false")) {
            if (enabled_seen++) { valid = 0; break; }
            mod->enabled = !strcmp(line, "enabled=true");
        } else if (!strncmp(line, "adventure.menu.empty=", 21)) {
            const char *value = line + 21;
            if (label_seen++ || strlen(value) != 5) { valid = 0; break; }
            for (unsigned i = 0; i < 5; i++) if (value[i] < 'A' || value[i] > 'Z') valid = 0;
            memcpy(mod->label, value, 6);
        } else { valid = 0; break; }
    }
    if (ferror(file)) valid = 0;
    fclose(file);
    if (!enabled_seen || (mod->enabled && !label_seen)) valid = 0;
    if (!valid) mod->enabled = 0;
    return valid;
}

static uint8_t cdi_text_mod_byte(CdiTextMod *mod, const uint8_t *ram,
                                 uint32_t size, uint32_t offset, uint8_t original) {
    if (!mod->enabled || !ram || offset >= size) return original;
    const char *source = "EMPTY";
    for (uint32_t i = 0; i < 5; i++) {
        if (original != (uint8_t)source[i] || offset < i) continue;
        uint32_t start = offset - i;
        if (size - start >= 6 && !memcmp(ram + start, source, 6)) {
            mod->hits++;
            return (uint8_t)mod->label[i];
        }
    }
    return original;
}
