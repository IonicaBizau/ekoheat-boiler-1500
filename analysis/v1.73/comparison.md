# Official v1.73 compared with supplied v1.72

This is a binary-derived comparison, not a vendor release note. Both input files were read only and remain unchanged. A separate [minimal v1.73 display-only derivative](../patched/v1.73/README.md) was created after this comparison.

## Image identity

| | v1.72 folder | v1.73 folder |
| --- | --- | --- |
| File | `Ecoheat_v1.72/DTX9003.uc3` | `DTX9003 v1.73/DTX9003.uc3` |
| Bytes | 450509 | 453229 |
| Embedded build date | Dec 3 2014 | Jul 13 2016 |
| SHA-256 | `b5ab1b7380f2486c29cf6708954cdb5bbaa2d7798fd0103f845fa254da51a5e8` | `e57bb9517c66e8f37ecb864daca5735bc14e3ef6a2614c94a962dc62809f2e3a` |
| Payload CRC32 | `0x42452353` | `0xA69EA7CF` |

The new file is 2720 bytes larger. Both match their stored big-endian CRC32 at offset `0x15`, covering bytes from `0x19` to EOF. Header bytes before the CRC are identical. Both contain big-endian AVR32 code, with payload mapping `VA = offset + 0x80007FE7`.

## Verified changes

### Low-fuel warning

The remaining-fuel decrement function changed from `0x80010DA4` to `0x80011170`. New code detects a downward crossing from at least 50000 to below 50000 in the stored remaining-fuel count, raises a warning/event flag, and formats a new localized `Hopper low on fuel!` message. Units are left as the exact internal count here rather than assuming a kilogram conversion.

The new event flag is RAM `0x231A`; display warning indication is RAM `0x538B`. The communication task at `0x80022E48` has a new event path for this flag, with `WARNING: %s` formatting. The main-screen acknowledgement path at `0x80016AAC` can dismiss the warning indication without requiring an active boiler fault. This is a new warning, not a demonstrated new shutdown rule.

Evidence: `decompiled/80011170.txt`, `80022e48.txt`, `80016aac.txt`; old `../ghidra/decompiled/80010da4.txt`; `strings.diff`.

### Expanded communication/status text

The transmit task (`0x800227EC` -> `0x80022E48`) adds warning transmission and additional formatted fields: `Hopper: %4.1f kg`, `Lux: %d`, `Return: %3.1f`, `Flue: %3.0f`, `HWT: %3.1f`, and boiler model labels. It uses these fields in the status assembly path. Transport/application compatibility has not been tested.

### Main-screen branding changed; startup logo preserved

The old 130×25 `ekopower` bitmap is no longer present. The new main screen uses an `Ekoheat` text widget and an adjacent dynamic text widget. Screen 21 moved from `0x8002D72C` (file `0x25745`) to `0x8002E108` (file `0x26121`). The new text begins at file `0x2613F`.

The 227×44 startup logo is byte-for-byte unchanged and remains bitmap 7 in startup screen 11. Of the 23 original raw bitmap assets, 22 are found unchanged in the new image. The deleted small logo shifts later bitmap indices; new index 11 is the old index 12, not a replacement logo.

New screen-pointer table: `0x8003A198`; bitmap-pointer table: `0x8004E9E4`. Evidence: `bitmap-comparison.json`, `new-asset-info.json`, `decompiled/8005e078.txt`, and original `../assets/README.md`.

### Pump-control changes

TimerTask (`0x8000B3F4` -> `0x8000B410`) adds a latch using boiler-water temperature divided by 100 and constants 5.0 and 10.0. The latch is set below 5°C and cleared at/above 10°C. In the relevant automatic-control branch, it forces the circulation-pump request on while set. The same branch also changes schedule/temperature-based pump conditions. This resembles frost protection, but that purpose is an interpretation; the thresholds and output assignment are present in the code.

The low-temperature latch is RAM `0x22E4`; pump request is RAM `0x5F01`; water-temperature value is RAM `0x50DC`. Existing inhibition branches still apply; this is not a claim that the pump runs unconditionally in every mode.

### Additional response to digital input GPIO 0x20

The processed input is RAM `0x50B3`. New edge handling appears in standby (`0x8000E47C`), running (`0x8000F64C`), and shutdown (`0x80010380`). Standby can request a start on its transition to zero; running can enter a standby-like mode on transition to one when a new countdown is zero. The shutdown path also reacts to that transition. The external device associated with this input has not been conclusively named, so it is not described as a thermostat or lid switch.

The one-second task also adds an error-3 assignment for a different input, RAM `0x50AF`, while the boiler is not off. The producer/electrical meaning of that signal remains unresolved.

### Calibration and idle behavior

The idle countdown in TimerTask now additionally requires calibration-accepted flag RAM `0x226C` to equal 1. The screen transition and backlight fades are still present; v1.73 does not incorporate the custom always-active-screen patch.

### Parameter and factory-profile changes

Factory profiles remain 188-byte records (`0xBC` stride). Old table `0x8002BBC4`; new table `0x8002C5A0`.

- For the four production profiles (indices 0–3), byte `+0x4A` changes from 70 to 90. This is the upper bound passed to the numeric editor for the DHW-temperature field (value byte `+0x4B`, still 60). It is an increased editing limit, not an automatic change of target to 90°C.
- For profile 3 (4000), startup fan base at `+0x66` changes 50 -> 40, and startup fan increment at `+0x67` changes 30 -> 25. These fields are used in the ignition fan commands. Other profiles retain these bytes.
- The configuration loader no longer forces the boiler-temperature working setting to 80 when the configuration mode byte `+0x83` is 1. It still preserves the configured temperature separately. This is a removed conditional override; its full effect depends on that operating mode.

Evidence: `profile-comparison.json`, old `80011da0.txt` / new `800121d0.txt`, numeric editor old `8001a008.txt` / new `8001a500.txt`, ignition old `8000eaf8.txt` / new `8000ed44.txt`, and configuration loader old `80011168.txt` / new `800115ac.txt`.

## Important rules that remain

| Behavior | v1.72 function | v1.73 function | Result |
| --- | --- | --- | --- |
| Ash-plate cycle | `0x80010DF4` | `0x80011238` | Opening counter still compared against configured deciseconds +100. Closing checks still use indices 30 and >35. |
| Ignition light threshold and ramp | `0x8000EAF8` | `0x8000ED44` | Detection at >=18; 240-second stabilization; low-light counter >29 in ramp. |
| Ignition retries | `0x80023754` | `0x80024100` | Three attempts before error 4; factory wait still 600 seconds in all five profiles. |
| Endstop-triggered recalibration | `0x8001F3DC` | `0x8001F978` | Three active transitions in a 5000-tick window still clear and save the calibration flag. |
| Idle screen | `0x8001E7E8` | `0x8001ED84` | Automatic transition still present. |

The subsystem state machine has an additional small change: its running-to-idle transition can now occur in boiler state 1 as well as state 0, with the standby flag set. See `decompiled/80024100.txt`.

## Method and limits

- Generated independent native SLEIGH disassembly and native Ghidra decompilation for the application-function prologues in the new image, plus targeted renderer functions.
- Compared ASCII string sequences, factory-table bytes, whole bitmap payloads, and relevant function bodies.
- `function-matches.json` and `diffs/` are heuristic triage aids. Address-masked similarity is not proof of equivalence; RAM locations and actual branch conditions must be read in the original outputs. Some decompiled argument lists are incomplete for soft-float, varargs, and indirect dispatch.
- Not every driver/library instruction or UI widget has been semantically compared. Unlisted changes may exist. No hardware behavior, vendor intent, or update acceptance is claimed.
- The existing custom derivative and patch script target the v1.72 source hash only. The combined v1.72 patch has not been ported to v1.73; old patch offsets must not be reused. The later minimal v1.73 display-only derivative uses independently identified offsets.

## Reproduce the decompilation

From the project root, using the native components already built under `analysis/ghidra/`:

```sh
python3 analysis/tools/decompile_functions.py --image analysis/v1.73/firmware.xml --out analysis/v1.73/decompiled --functions analysis/v1.73/functions.json --limit 0x80026b00
python3 analysis/tools/compare_decompiled.py
```

The XML image was generated directly from the new file's bytes after its 25-byte wrapper and loaded at `0x80008000`. The default Ghidra path in the helper can be overridden with `--ghidra`.
