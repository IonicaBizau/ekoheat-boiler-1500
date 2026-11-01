# v1.73: keep the screen awake and give the ash plate more time

For preparing the USB drive and using the controller update menu, see [Updating the boiler software](../../../docs/updating-firmware.md).

The combined patch now displays **v1.73.42**. I changed the version format from `v%d.%02d  %s` to `v%d.%02d.42 %s` inside its original 16-byte allocation, including the terminating NUL and padding. The build date remains visible; file size, pointers, numeric version arguments, and update-header metadata stay unchanged. This is a display revision label, not a new vendor release or bootloader version. The earlier v1.73 screen-only image keeps its original label.

I added the same 30-second ash-plate opening allowance as the v1.72 patch, together with the screen-awake change. The original firmware and supplied license file stay untouched.

```sh
python3 analysis/tools/patch_v173_30s.py
python3 analysis/tools/verify_patch.py --version 1.73
```

Output: [`DTX9003_no_idle_clock_30s.uc3`](DTX9003_no_idle_clock_30s.uc3), based on `DTX9003 v1.73/DTX9003.uc3`.

| Purpose | Address | File offset | Original bytes | Patched bytes |
| --- | --- | --- | --- | --- |
| Keep screen awake | `0x8000BA8E` | `0x3AA7` | `30 08` | `36 48` |
| Allow 300 extra deciseconds for opening | `0x8001136A` | `0x9383` | `29 C8 10 39 E0 8A 00 13` | `F0 C8 FE D4 12 38 C1 22` |
| Update payload CRC32 | Header | `0x15` | `A6 9E A7 CF` | `D5 04 F4 AC` |

The opening check now reports a fault when `counter > configured_movement_deciseconds + 300`, up from `+100`. The replacement uses `SUB R8,R8,-300`, `CP.W R8,R9`, and `BRHS 0x80011394`. Configuration and counter values are zero-extended 16-bit values, so the unsigned comparison keeps the intended ordering throughout their ranges.

This allows **30 extra seconds**, rather than limiting total opening time to 30 seconds. The original wait/check order adds a nominal 0.2 seconds: a 10-second movement setting gives a nominal opening fault point of 40.2 seconds. Scheduling can affect physical timing. Closing checks, endstop handling, and ignition behavior are unchanged.

The [manifest](DTX9003_no_idle_clock_30s.json) records each patch and changed byte. The [verification results](verification-30s.json) cover checksums, unchanged regions, file size, decoded instructions, branch target, and 326777 boundary comparisons. Native SLEIGH output is in [opening-original.tsv](opening-original.tsv) and [opening-patched.tsv](opening-patched.tsv); the [patched decompilation](decompiled-80011238.txt) independently shows the `+300` check.

- Output SHA-256: `7e5a1a3a980c00eb719fa74ac8b54d012cb62402bcdd670088ad4a67652fae85`
- Payload CRC32: `0xD504F4AC`
- Size: 453229 bytes, unchanged.

I have checked this offline. I have not flashed it, tested physical motor/display behavior, or verified bootloader/license-file acceptance.

## Earlier screen-only patch

The earlier output below is still available and retains the original 10-second opening allowance.

Output: `DTX9003_no_idle_clock.uc3`, derived from `DTX9003 v1.73/DTX9003.uc3`.
I left the original untouched. This patch changes just two payload bytes and the CRC32 field.

| Address | File offset | Original | Patched |
| --- | --- | --- | --- |
| `0x8000BA8E` | `0x3AA7` | `30 08` (`MOV R8,0`) | `36 48` (`MOV R8,100`) |

TimerTask (`0x8000B410`) still decrements inactivity counter RAM `0x74C` under its existing conditions. On expiry, the patched instruction requests brightness 100 rather than 0 at RAM `0x2336`. The unchanged pointer at `0x8000BD7C` identifies that destination, and the following `ST.H R9[0],R8` is preserved.

BacklightTask (`0x80008348`) processes the request. GUITask (`0x8001ED84`) automatically selects clock screen state 1 when display state RAM `0x2331` reaches zero. Keeping the expiry request at 100 prevents this automatic idle fade and clock-screen transition. The timer still expires, preserving existing dialog timeouts. Other explicit screen/brightness requests remain intact.

No ash-movement, combustion, sensor or fault-handling changes are included.

Reproduce from the project root:

```sh
python3 analysis/tools/patch_v173_no_idle_clock.py
```

The script checks the exact source SHA-256, source CRC, surrounding instruction bytes, destination pointer, unchanged regions, output CRC and file size, and preservation of the source. The JSON manifest records hashes and every changed byte. Native Ghidra SLEIGH disassembly is in `idle-expiry-original.tsv` and `idle-expiry-patched.tsv`. Native patched decompilation is in `decompiled-8000b410.txt`.

I have only checked this offline. I have not tested it on the controller, checked bootloader acceptance, or verified the display behavior on hardware.
