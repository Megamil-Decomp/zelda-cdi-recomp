/* Author-written synthetic m68k fixture. No game or BIOS bytes. */
#include "code_generator.h"
#include "codegen_diag.h"
#include "function_finder.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void put_word(uint8_t *image, unsigned at, unsigned value) {
    image[at] = value >> 8;
    image[at + 1] = value;
}

int main(int argc, char **argv) {
    if (argc != 3) return 2;
    int external = !strcmp(argv[2], "external");
    uint8_t image[0x100] = {0};
    /* JMP (0,PC,D0.W): base = the JMP extension word at 0x42.
     * A speculative zero-offset table row would seed that extension as code.
     * Two ORI-looking rows lead into illegal ORI.B #1,(d16,PC).
     * The actual externally supplied entry at 0x60 is MOVEQ #7; RTS. */
    put_word(image, 0x40, 0x4efb);
    put_word(image, 0x42, external ? 0x0006 : 0x0000);
    if (external) {
        /* Genuine table outside the JMP: base0x48, rows ->0x60,0x64.
         * -32768 is an out-of-range terminator for the finite heuristic. */
        put_word(image, 0x48, 0x0018);
        put_word(image, 0x4a, 0x001c);
        put_word(image, 0x4c, 0x8000);
        put_word(image, 0x64, 0x7209);
        put_word(image, 0x66, 0x4e75);
    } else {
        put_word(image, 0x44, 0x0008);
        put_word(image, 0x46, 0x003a);
        put_word(image, 0x48, 0x0001);
        put_word(image, 0x4a, 0x0010);
        put_word(image, 0x4c, 0x4e75);
    }
    put_word(image, 0x60, 0x7007);
    put_word(image, 0x62, 0x4e75);
    GenesisRom rom = {0};
    rom.rom_data = image;
    rom.rom_size = sizeof image;
    rom.initial_pc = 0x40;
    uint32_t entry = 0x40;
    GameConfig config = {0};
    game_config_init_empty(&config);
    config.function_aliases = true;
    config.async_resume_entries = true;
    config.extra_funcs = &entry;
    config.extra_func_count = 1;
    ProtectedRange header = {0, 0x40};
    config.protected_ranges = &header;
    config.protected_range_count = 1;
    FunctionList functions = {0};
    function_finder_run_module(&rom, &functions, &config);
    AnnotationTable annotations = {0};
    char full[1200], dispatch[1200];
    snprintf(full, sizeof full, "%s/full.c", argv[1]);
    snprintf(dispatch, sizeof dispatch, "%s/dispatch.c", argv[1]);
    int emitted = codegen_emit_module(&rom, &functions, full, dispatch,
                                     &annotations, &config, "fixture");
    int diagnostics = codegen_diag_total();
    codegen_diag_print_summary(stderr);
    function_list_free(&functions);
    printf("fixture_emitted=%d diagnostics=%d\n", emitted, diagnostics);
    return emitted && diagnostics == 0 ? 0 : 1;
}
