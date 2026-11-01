# v1.72: keep the screen awake and give the ash plate more time

For preparing the USB drive and using the controller update menu, see [Updating the boiler software](../../../docs/updating-firmware.md).

The combined patch now displays **v1.72.42**. I changed the version format from `v%d.%02d  %s` to `v%d.%02d.42 %s` inside its original 16-byte allocation, including the terminating NUL and padding. The build date remains visible; file size, pointers, numeric version arguments, and update-header metadata stay unchanged. This is a display revision label, not a new vendor release or bootloader version.

Output: `DTX9003.uc3`

Created from `DTX9003 v1.72/DTX9003.uc3`. I left the original untouched. I have checked this patch offline, but have not flashed it or run it on the controller.

## Changes

| Purpose | Machine address | File offset | Original bytes | Patched bytes |
| --- | --- | --- | --- | --- |
| Keep display active at inactivity expiry | `0x8000B964` | `0x397D` | `30 08` | `36 48` |
| Increase opening tolerance to 300 deciseconds | `0x80010F26` | `0x8F3F` | `29 C8 10 39 E0 8A 00 13` | `F0 C8 FE D4 12 38 C1 22` |
| Payload CRC32, big endian | Header | `0x15` | `42 45 23 53` | `DE BB 4F C5` |

Address mapping: `VA = file_offset + 0x80008000 - 25`.

### Automatic clock-screen transition

The touch handler `0x800164E4` resets the inactivity counter at RAM `0x724` to 240. Timer task `0x8000B3F4` conditionally decrements it once per nominal second. On expiry, the original code stores zero into the display brightness request at RAM `0x228A`.

Backlight task `0x80008348` moves toward that request. GUI task `0x8001E7E8` checks the resulting display state at RAM `0x2285`; when it reaches state zero, the GUI saves the current screen and switches to screen state 1, rendered by `0x800174D4` using screen resource `0x4C`.

The patch changes the inactivity-expiry value to 100. This prevents the automatic idle blanking that triggers the clock screen and keeps the current screen active. The timer itself still expires, retaining its uses in modal-dialog timeouts. Explicit screen selection and other brightness requests are not globally removed.

Evidence: original decompilations in `../../ghidra/decompiled/800164e4.txt`, `8000b3f4.txt`, `80008348.txt`, `8001e7e8.txt`, and `800174d4.txt`; patched timer decompilation in `decompiled-8000b3f4.txt`.

### Opening tolerance

Original instructions:

```text
80010F26  SUB R8,-100
80010F28  CP.W R9,R8
80010F2A  BRle 0x80010F50
```

Replacement, occupying the same eight bytes:

```text
80010F26  SUB R8,R8,-300
80010F2A  CP.W R8,R9
80010F2C  BRHS 0x80010F50
```

The replacement adds 300, swaps comparison operands, and branches to the same continuation address when the counter is at or below the threshold. Both operands are nonnegative: the configuration and counter are zero-extended 16-bit values, and the addition produces at most 65835. Therefore the unsigned comparison preserves the intended ordering across their entire ranges.

The opening loop waits 100 ticks, then tests a counter initially zero. The error condition is now `counter > movement_deciseconds + 300`. The first failing iteration nominally occurs after `movement_seconds + 30.2` seconds, preserving the original two-iteration timing offset. This is the opening allowance, not a 30-second total movement time. For a configured movement of 10 seconds, the nominal failure point is 40.2 seconds. Scheduling and independent sensor/output processing affect observed physical timing.

Closing logic, early opening-endstop stopping, and error handling are unchanged. No new settings field was added.

Evidence: `../../evidence/ash-cycle-disassembly.tsv`, `../../ghidra/decompiled/80010df4.txt`, and `decompiled-80010df4.txt`.

## Validation and reproduction

Run from the project root:

```sh
python3 analysis/tools/patch_firmware.py
python3 analysis/tools/verify_patch.py
```

The patch script refuses any input whose SHA-256 differs from the analyzed image. Verification checks unchanged regions, instruction encoding, branch destination, CRC, and 326777 boundary comparisons across every 16-bit movement value. Ghidra's native SLEIGH decoder also independently decoded the patched instructions, and its decompiler reconstructed the modified routines.

- Source SHA-256: `b5ab1b7380f2486c29cf6708954cdb5bbaa2d7798fd0103f845fa254da51a5e8`
- Derivative SHA-256: `1f35cad23f091dacd35a45dc1048ac0e409acaa5bcdc9c0aa20b3870e3e6ba19`
- Size: 450509 bytes, unchanged.
- CRC32 of bytes from offset 25 through EOF: `0xDEBB4FC5`.

See the accompanying JSON manifest and `verification.json` for machine-readable results. Static checks do not establish controller bootloader acceptance or physical motor/display behavior. Opaque header metadata remains unchanged.
