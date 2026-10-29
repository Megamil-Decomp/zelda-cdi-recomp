/* Author-written CPU/MMIO-boundary fixtures; no BIOS or game data. */
#include "m68k_interp.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

M68KState g_cpu;
uint8_t g_ram0[CDI_RAM0_SIZE], g_ram1[CDI_RAM1_SIZE], g_rom[CDI_ROM_SIZE];
uint32_t g_cycle_accumulator, g_last_access_addr, g_fault_addr;
uint16_t g_fault_opcode;
int g_halted;
static unsigned csr_reads, invalid_reads, exceptions;
static uint8_t synthetic_csr = 0xa5;

static uint8_t *ordinary(uint32_t address) {
    if (address < CDI_RAM0_SIZE) return g_ram0 + address;
    if (address >= CDI_RAM1_BASE && address - CDI_RAM1_BASE < CDI_RAM1_SIZE)
        return g_ram1 + address - CDI_RAM1_BASE;
    if (address >= CDI_ROM_BASE && address < CDI_MCD212_BASE)
        return g_rom + address - CDI_ROM_BASE;
    return NULL;
}
uint8_t m68k_read8(uint32_t address) {
    g_last_access_addr = address;
    uint8_t *p = ordinary(address);
    if (p) return *p;
    if (address == CDI_MCD212_BASE || address == CDI_MCD212_BASE + 1) {
        uint8_t value = synthetic_csr;
        csr_reads++;
        synthetic_csr = 0;
        return value;
    }
    invalid_reads++;
    if (address == 0x600000 && m68k_interp_bus_error(address)) return 0;
    fprintf(stderr, "forbidden synthetic bus read at %08x\n", address);
    exit(90); /* Controlled fixture failure without a host crash report. */
}
uint16_t m68k_read16(uint32_t a) { return (uint16_t)((m68k_read8(a) << 8) | m68k_read8(a + 1)); }
uint32_t m68k_read32(uint32_t a) { return ((uint32_t)m68k_read16(a) << 16) | m68k_read16(a + 2); }
void m68k_write8(uint32_t a, uint8_t v) { uint8_t *p = ordinary(a); if (!p) abort(); *p = v; }
void m68k_write16(uint32_t a, uint16_t v) { m68k_write8(a, v >> 8); m68k_write8(a + 1, v); }
void m68k_write32(uint32_t a, uint32_t v) { m68k_write16(a, v >> 16); m68k_write16(a + 2, v); }
void m68k_set_sr(uint16_t v) { g_cpu.SR = v; }
void m68k_raise_exception_frame(uint8_t vector) { if (vector != 2) abort(); exceptions++; g_cpu.PC = 0x200; }
void debug_trace_block(void) {}
void debug_trace_interp(uint32_t pc) { (void)pc; }
void debug_record_indirect_target(uint32_t pc) { (void)pc; }
int dispatch_has_addr(uint32_t pc) { (void)pc; return 0; }
void genesis_reset_devices(void) { abort(); }
void genesis_stop_until_interrupt(uint16_t sr) { (void)sr; abort(); }
void mcd212_tick(uint32_t cycles) { (void)cycles; }
void runtime_defer_exception_cycles(uint32_t cycles) { if (cycles != 158) abort(); }

static void word(uint32_t address, uint16_t value) {
    uint8_t *p = ordinary(address);
    if (!p || !ordinary(address + 1)) abort();
    p[0] = value >> 8;
    p[1] = value;
}
#define REQUIRE(condition) do { if (!(condition)) { fprintf(stderr, "fixture failed at line %d\n", __LINE__); return 1; } } while (0)
int main(int argc, char **argv) {
    if (argc != 2) return 2;
    M68KInstr instruction;
    g_last_access_addr = 0x123456;
    if (!strcmp(argv[1], "short")) {
        g_cpu.PC = CDI_MCD212_BASE - 2;
        word(g_cpu.PC, 0x4e71); /* NOP, complete before the MMIO boundary. */
        REQUIRE(m68k_interp_decode_at(g_cpu.PC, &instruction) == 2);
        REQUIRE(g_last_access_addr == 0x123456);
        REQUIRE(m68k_interp_step() == M68KI_OK);
        REQUIRE(g_cpu.PC == CDI_MCD212_BASE);
        REQUIRE(csr_reads == 0 && invalid_reads == 0 && synthetic_csr == 0xa5);
    } else if (!strcmp(argv[1], "invalid")) {
        g_cpu.PC = CDI_MCD212_BASE + 2;
        REQUIRE(m68k_interp_decode_at(g_cpu.PC, &instruction) == 0);
        REQUIRE(m68k_interp_step() == M68KI_HALT_BADADDR);
        REQUIRE(g_m68ki_bad_pc == CDI_MCD212_BASE + 2);
        REQUIRE(csr_reads == 0 && invalid_reads == 0 && synthetic_csr == 0xa5);
    } else if (!strcmp(argv[1], "truncated")) {
        g_cpu.PC = CDI_MCD212_BASE - 2;
        word(g_cpu.PC, 0x303c); /* MOVE.W #immediate,D0; extension is unavailable. */
        REQUIRE(m68k_interp_decode_at(g_cpu.PC, &instruction) == 0);
        REQUIRE(m68k_interp_step() == M68KI_HALT_BADADDR);
        REQUIRE(g_cpu.PC == CDI_MCD212_BASE - 2);
        REQUIRE(g_m68ki_bad_op == 0x303c);
        REQUIRE(csr_reads == 0 && invalid_reads == 0 && synthetic_csr == 0xa5);
    } else if (!strcmp(argv[1], "ram-end")) {
        g_cpu.PC = CDI_RAM0_SIZE - 2;
        word(g_cpu.PC, 0x4e71);
        REQUIRE(m68k_interp_step() == M68KI_OK);
        REQUIRE(g_cpu.PC == CDI_RAM0_SIZE);
        REQUIRE(m68k_interp_step() == M68KI_HALT_BADADDR);
        REQUIRE(invalid_reads == 0);
    } else if (!strcmp(argv[1], "operand-fault")) {
        g_cpu.PC = 0x100;
        g_cpu.A[0] = 0x600000;
        g_cpu.D[0] = 0xdeadbeef;
        word(g_cpu.PC, 0x1010); /* MOVE.B (A0),D0: a real operand bus error. */
        REQUIRE(m68k_interp_step() == M68KI_OK);
        REQUIRE(exceptions == 1 && invalid_reads == 1 && g_fault_addr == 0x600000);
        REQUIRE(g_cpu.PC == 0x200 && g_cpu.D[0] == 0xdeadbeef);
    } else if (!strcmp(argv[1], "ordinary")) {
        g_cpu.PC = 0x100;
        word(0x100, 0x303c); word(0x102, 0x1234); /* MOVE.W #$1234,D0 */
        REQUIRE(m68k_interp_step() == M68KI_OK);
        REQUIRE(g_cpu.PC == 0x104 && g_cpu.D[0] == 0x1234);
        REQUIRE(csr_reads == 0 && invalid_reads == 0);
    } else return 2;
    puts("synthetic interpreter fetch passed");
    return 0;
}
