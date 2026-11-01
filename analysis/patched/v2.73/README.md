# v1.73: keep the screen awake and give the ash plate more time

For preparing the USB drive and using the controller update menu, see [Updating the boiler software](../../../docs/updating-firmware.md).

The combined patch displays **v2.73**. At `0x80016780` (file offset `0xE799`), `MOV R8,1` (`30 18`) becomes `MOV R8,2` (`30 28`) for the displayed major-version argument. The original format `v%d.%02d  %s`, minor version 73, build date, file size, pointers, and update-header metadata remain unchanged. This is a custom display label, not a vendor release.

I added the same 30-second ash-plate opening allowance as the v1.72 patch, together with the screen-awake change. The original firmware and supplied license file stay untouched.

```sh
python3 analysis/tools/patch_v173_30s.py
python3 analysis/tools/verify_patch.py --version 1.73
```

Output: [`DTX9003.uc3`](DTX9003.uc3), based on `DTX9003 v1.73/DTX9003.uc3`.

| Purpose | Address | File offset | Original bytes | Patched bytes |
| --- | --- | --- | --- | --- |
| Keep screen awake | `0x8000BA8E` | `0x3AA7` | `30 08` | `36 48` |
| Allow 300 extra deciseconds for opening | `0x8001136A` | `0x9383` | `29 C8 10 39 E0 8A 00 13` | `F0 C8 FE D4 12 38 C1 22` |
| Update payload CRC32 | Header | `0x15` | `A6 9E A7 CF` | `DD 3E 71 AC` |

The opening check now reports a fault when `counter > configured_movement_deciseconds + 300`, up from `+100`. The replacement uses `SUB R8,R8,-300`, `CP.W R8,R9`, and `BRHS 0x80011394`. Configuration and counter values are zero-extended 16-bit values, so the unsigned comparison keeps the intended ordering throughout their ranges.

This allows **30 extra seconds**, rather than limiting total opening time to 30 seconds. The original wait/check order adds a nominal 0.2 seconds: a 10-second movement setting gives a nominal opening fault point of 40.2 seconds. Scheduling can affect physical timing. Closing checks, endstop handling, and ignition behavior are unchanged.

The [manifest](DTX9003.json) records each patch and changed byte. The [verification results](verification.json) cover checksums, unchanged regions, file size, decoded instructions, branch target, and 326777 boundary comparisons. Native SLEIGH output is in [opening-original.tsv](opening-original.tsv) and [opening-patched.tsv](opening-patched.tsv); the [patched decompilation](decompiled-80011238.txt) independently shows the `+300` check.

- Output SHA-256: `d14f1f5cd2f2008e008cc78534dda1e8b4194b0005e8f403c999b14bb80f5471`
- Payload CRC32: `0xDD3E71AC`
- Size: 453229 bytes, unchanged.

I have checked this offline. I have not flashed it, tested physical motor/display behavior, or verified bootloader/license-file acceptance.

## Clock-screen recheck

The v1.73 timer task (`0x8000B410`) decrements inactivity RAM `0x74C` and originally writes zero to brightness request `0x2336` on expiry. The patch at `0x8000BA8E` writes 100 instead. Backlight task `0x80008348` approaches `100 - request`; its zero-display state (`0x2331 == 0`) triggers GUI task `0x8001ED84` to save the current screen and select clock state 1. Keeping the request at 100 prevents this automatic idle path. The timer continues to expire for other UI uses.

Rechecked against the original [timer](../../v1.73/decompiled/8000b410.txt), [backlight](../../v1.73/decompiled/80008348.txt), and [GUI](../../v1.73/decompiled/8001ed84.txt) decompilations and the patched instruction/store bytes. Explicit brightness writes in GUI transitions and service commands (`0x800222AC`) remain; this patch disables the automatic inactivity transition, not every possible way to select the clock. Hardware execution remains untested.
