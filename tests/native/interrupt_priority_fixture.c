/* Authored synthetic CPU interrupt scenarios; no BIOS, disc or game code. */
#include "cdi_runtime.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static uint8_t memory[0x10000];
uint32_t g_last_access_addr;
void mcd212_tick(uint32_t cycles) { (void)cycles; }
void debug_record_irq_raise(uint8_t level) { (void)level; }

uint16_t m68k_read16(uint32_t address) {
    if (address >= sizeof memory - 1u) exit(80);
    return (uint16_t)((memory[address] << 8) | memory[address + 1u]);
}
uint32_t m68k_read32(uint32_t address) {
    return ((uint32_t)m68k_read16(address) << 16) | m68k_read16(address + 2u);
}
void m68k_write16(uint32_t address, uint16_t value) {
    if (address >= sizeof memory - 1u) exit(81);
    memory[address] = (uint8_t)(value >> 8);
    memory[address + 1u] = (uint8_t)value;
}
void m68k_write32(uint32_t address, uint32_t value) {
    m68k_write16(address, (uint16_t)(value >> 16));
    m68k_write16(address + 2u, (uint16_t)value);
}

#define CHECK(condition) do { if (!(condition)) { \
    fprintf(stderr, "line %d: %s (SR=%04x PC=%06x SP=%06x)\n", \
            __LINE__, #condition, g_cpu.SR, g_cpu.PC, g_cpu.A[7]); \
    return 1; } } while (0)

static int take_irq(void) {
    if (setjmp(g_recomp_irq_env)) return 1;
    recomp_take_irq();
    return 0;
}

int main(int argc, char **argv) {
    if (argc != 2) return 2;
    memset(&g_cpu, 0, sizeof g_cpu);
    /* Trace on, user mode, IPL 2, distinctive CCR; separate user/super stacks. */
    g_cpu.SR = 0x8215u;
    g_cpu.A[7] = 0x5000u;
    g_cpu.SSP = 0x6000u;
    g_cpu.PC = 0x2000u;
    g_recomp_irq_armed = 1;
    m68k_write32(65u * 4u, 0x3000u);
    m68k_write32(66u * 4u, 0x4000u);
    m68k_write32(59u * 4u, 0x3800u); /* On-chip level 3 vector. */

    if (!strcmp(argv[1], "masked")) {
        cdi_irq_raise_vector(2, 65);
        CHECK(!take_irq());
        CHECK(g_cpu.SR == 0x8215u && g_cpu.PC == 0x2000u);
        CHECK(g_cpu.A[7] == 0x5000u && (recomp_pending_irq_mask() & 4u));
        return 0;
    }
    if (!strcmp(argv[1], "unarmed")) {
        g_recomp_irq_armed = 0;
        cdi_irq_raise_vector(4, 65);
        CHECK(!take_irq());
        CHECK(g_cpu.SR == 0x8215u && g_cpu.A[7] == 0x5000u);
        CHECK(recomp_pending_irq_mask() & 16u);
        return 0;
    }
    if (!strcmp(argv[1], "onchip")) {
        cdi_irq_raise_onchip_level(3);
        CHECK(take_irq());
        CHECK(g_cpu.SR == 0x2315u && g_cpu.PC == 0x3800u);
        CHECK(m68k_read16(g_cpu.A[7]) == 0x8215u);
        CHECK(m68k_read16(g_cpu.A[7] + 6u) == 59u * 4u);
        return 0;
    }

    cdi_irq_raise_vector(4, 65);
    CHECK(take_irq());
    if (!strcmp(argv[1], "entry")) {
        CHECK(g_cpu.SR == 0x2415u && g_cpu.PC == 0x3000u);
        CHECK(g_cpu.A[7] == 0x5ff8u && g_cpu.USP == 0x5000u);
        CHECK(m68k_read16(0x5ff8u) == 0x8215u);
        CHECK(m68k_read32(0x5ffau) == 0x2000u);
        CHECK(m68k_read16(0x5ffeu) == 65u * 4u);
        return 0;
    }
    if (!strcmp(argv[1], "same-level")) {
        cdi_irq_raise_vector(4, 65);
        CHECK(!take_irq());
        CHECK(g_cpu.A[7] == 0x5ff8u && (recomp_pending_irq_mask() & 16u));
        return 0;
    }
    if (!strcmp(argv[1], "higher-level")) {
        cdi_irq_raise_vector(6, 66);
        CHECK(take_irq());
        CHECK(g_cpu.SR == 0x2615u && g_cpu.PC == 0x4000u);
        CHECK(g_cpu.A[7] == 0x5ff0u);
        CHECK(m68k_read16(0x5ff0u) == 0x2415u);
        CHECK(m68k_read32(0x5ff2u) == 0x3000u);
        return 0;
    }
    if (!strcmp(argv[1], "restore")) {
        uint16_t saved_sr = m68k_read16(g_cpu.A[7]);
        uint32_t saved_pc = m68k_read32(g_cpu.A[7] + 2u);
        g_cpu.A[7] += 8u;
        m68k_set_sr(saved_sr); /* Consume the frame with the runtime SR API. */
        g_cpu.PC = saved_pc;
        CHECK(g_cpu.SR == 0x8215u && g_cpu.A[7] == 0x5000u);
        CHECK(g_cpu.SSP == 0x6000u && g_cpu.PC == 0x2000u);
        cdi_irq_raise_vector(4, 65);
        CHECK(take_irq());
        CHECK(g_cpu.SR == 0x2415u && g_cpu.A[7] == 0x5ff8u);
        return 0;
    }
    return 2;
}
