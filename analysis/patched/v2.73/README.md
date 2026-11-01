# Custom v2.73: screen awake, longer ash-plate allowance, five startup attempts

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
| Five total normal startup attempts | `0x80024440` | `0x1C459` | `30 28` | `30 48` |
| Preserve special startup timeout behavior | `0x8000EE0C` | `0x6E25` | `30 38` | `30 58` |
| Update payload CRC32 | Header | `0x15` | `A6 9E A7 CF` | `3D A5 8A 4D` |

The opening check now reports a fault when `counter > configured_movement_deciseconds + 300`, up from `+100`. The replacement uses `SUB R8,R8,-300`, `CP.W R8,R9`, and `BRHS 0x80011394`. Configuration and counter values are zero-extended 16-bit values, so the unsigned comparison keeps the intended ordering throughout their ranges.

This allows **30 extra seconds**, rather than limiting total opening time to 30 seconds. The original wait/check order adds a nominal 0.2 seconds: a 10-second movement setting gives a nominal opening fault point of 40.2 seconds. Scheduling can affect physical timing. Closing checks and endstop handling are unchanged. This build also increases normal startup attempts to five, as described below.

The [manifest](DTX9003.json) records each patch and changed byte. The [verification results](verification.json) cover checksums, unchanged regions, file size, decoded instructions, branch target, and 326777 boundary comparisons. Native SLEIGH output is in [opening-original.tsv](opening-original.tsv) and [opening-patched.tsv](opening-patched.tsv); the [patched decompilation](decompiled-80011238.txt) independently shows the `+300` check.

- Output SHA-256: `63e995560940e029422cd77bdbbb4aefc0e6fe24f116692677b1dfb324d4e546`
- Payload CRC32: `0x3DA58A4D`
- Size: 453229 bytes, unchanged.

I have checked this offline. I have not flashed it, tested physical motor/display behavior, or verified bootloader/license-file acceptance.

## Clock-screen recheck

The v1.73 timer task (`0x8000B410`) decrements inactivity RAM `0x74C` and originally writes zero to brightness request `0x2336` on expiry. The patch at `0x8000BA8E` writes 100 instead. Backlight task `0x80008348` approaches `100 - request`; its zero-display state (`0x2331 == 0`) triggers GUI task `0x8001ED84` to save the current screen and select clock state 1. Keeping the request at 100 prevents this automatic idle path. The timer continues to expire for other UI uses.

Rechecked against the original [timer](../../v1.73/decompiled/8000b410.txt), [backlight](../../v1.73/decompiled/80008348.txt), and [GUI](../../v1.73/decompiled/8001ed84.txt) decompilations and the patched instruction/store bytes. Explicit brightness writes in GUI transitions and service commands (`0x800222AC`) remain; this patch disables the automatic inactivity transition, not every possible way to select the clock. Hardware execution remains untested.

## Five startup attempts

At the user's request, normal startup now allows **five total attempts** (the initial attempt plus four retries), instead of three. The incremented counter is compared with 4 instead of 2 at `0x80024440`, so error 4 is raised on the fifth failed wait. The configured wait per attempt is unchanged; factory profiles specify 600 seconds, so five waits can total roughly 50 minutes, excluding charging and scheduling overhead. This also extends possible ignition operation; the igniter's permitted duty cycle has not been verified.

The special startup path selected by `0x22F3 == 2` originally seeded the counter to the exhausted limit 3. Its seed is now 5 at `0x8000EE0C`, preserving its first-timeout failure rather than giving it extra retries. Its internal displayed attempt count can consequently differ.

The separate fuel-charge gate (`counter < 2`) stays intact. Attempts three through five bypass the initial charging setup, following the original third attempt's path. No new full or quarter fuel charges are introduced by this patch, although physical feed behavior is not hardware-tested. Light thresholds, configured wait, fan instructions, error handling, and the startup-ramp low-light failure are unchanged.

Verification checks exactly five timeout iterations from counter zero, special-path first-timeout failure, and that both routines differ only at these two instructions. Independent native SLEIGH [limit decoding](startup-limit-patched.tsv) and [special-path decoding](startup-special-patched.tsv), plus [state-machine decompilation](decompiled-80024100.txt) and [ignition decompilation](decompiled-8000ed44.txt), confirm the changed conditions. This is static verification, not a combustion or igniter-duty validation.

The display label remains **v2.73**. To distinguish this five-attempt rebuild from the earlier three-attempt v2.73 file, use the SHA-256 above. The [update investigation](../../update-investigation.md) has the load-failure findings; this rebuild is not a proven fix for that report.
