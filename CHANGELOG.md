# Changelog

## Minimal v1.73 display patch — 2026-11-01

- Prevent automatic idle clock-screen switching by changing `MOV R8,0` to `MOV R8,100` at `0x8000BA8E` (file offset `0x3AA7`).
- Two payload bytes and the CRC32 field change; file size and original source are preserved.
- No ash-movement or combustion changes are included.
- SHA-256: `dec5a6496a4688258a0566d9b33cdf61f9497d18912310e097b71bf91972503e`.
- Payload CRC32: `0xC097A83F`.
- Static source-hash, checksum, unchanged-region, native disassembly and decompilation checks passed. No controller execution or flashing performed.

See [minimal v1.73 patch](analysis/patched/v1.73/README.md) and [reproduction script](analysis/tools/patch_v173_no_idle_clock.py).

## Official v1.73 — compared with v1.72

Binary-derived findings from `DTX9003 v1.73/DTX9003.uc3`. Embedded build date: **2016-07-13**, versus **2014-12-03** in the supplied v1.72. This is not a vendor-published release note.

### Added

- **Low-fuel warning:** a downward crossing of 50000 internal remaining-fuel units triggers the new “Hopper low on fuel!” warning and a warning notification path. The warning can be acknowledged independently of an active fault.
- **Richer communication/status messages:** added warning text and fields for hopper quantity, light level, return/flue/hot-water temperatures, and boiler model.
- **Low-temperature pump override:** added a latch that requests the circulation pump below 5°C and clears at/above 10°C within the relevant automatic-control branch. This appears to serve frost protection; that purpose is inferred.
- **Digital-input edge handling:** additional start/standby/shutdown reactions to processed input GPIO `0x20`. The external device connected to this input has not been conclusively identified.

### Changed

- **Runtime branding:** replaced the small top-left `ekopower` bitmap with an `Ekoheat` text widget and adjacent dynamic text. The large startup logo is unchanged.
- **DHW temperature editor:** raised the upper editing limit from 70°C to 90°C in the four production profiles; the factory value remains 60°C.
- **4000-profile startup fan values:** base changed from 50 to 40, increment from 30 to 25.
- **Configuration loading:** removed the conditional override that forced the boiler-temperature working value to 80 in one configuration mode.
- **Idle timer:** countdown now additionally requires the saved touchscreen-calibration flag to be accepted.
- **Subsystem transition:** with the standby flag set, the running subsystem can transition to idle in boiler state 1 as well as state 0.

### Verified unchanged

- Ash-plate opening allowance remains **10 seconds** beyond the configured duration, with the original check-order offset. Closing sensor checks remain the same.
- Ignition still uses the **18-lux threshold**, three attempts, four-minute stabilization, and startup-ramp low-light failure condition. Factory ignition wait remains 600 seconds per attempt.
- The ash-endstop sequence that requests touchscreen recalibration remains present.
- Automatic clock-screen switching remains present.
- The startup logo and 21 other original bitmap assets are byte-for-byte unchanged; the old small runtime logo is absent.

### Analysis and compatibility

- Image size: **453229 bytes**, an increase of 2720 bytes.
- SHA-256: `e57bb9517c66e8f37ecb864daca5735bc14e3ef6a2614c94a962dc62809f2e3a`.
- Stored payload CRC32 `0xA69EA7CF` verified.
- The v1.72 combined patch has not been ported as a whole. A separate minimal v1.73 display-only patch is documented above; v1.72 offsets must not be reused for v1.73.
- Static comparison only; this list covers verified findings, not every possible driver or library change.

See [v1.73 comparison and evidence](analysis/v1.73/comparison.md) for function addresses, data offsets, original/new decompilations, and unresolved details.

## Custom patch — 2026-10-30

Based on the firmware supplied in `DTX9003 v1.72/DTX9003.uc3`.

### Changed

- Prevented the automatic idle clock-screen transition by keeping the display brightness request at 100 when the inactivity timer expires, instead of requesting blanking. The inactivity timer itself still expires for other UI uses.
- Increased the ash-plate opening allowance from 10 to 30 seconds beyond the configured movement duration. The existing loop/check order remains, giving a nominal failure point of configured duration plus 30.2 seconds.
- Recalculated the firmware payload CRC32.

### Validation

- Original firmware preserved; derivative created at `analysis/patched/DTX9003_no_idle_clock_30s.uc3`.
- File size unchanged: 450509 bytes.
- Patched instruction decoding and decompilation checked with Ghidra's native SLEIGH/decompiler components.
- Checksum, unchanged regions, branch destination, and 326777 boundary comparisons passed.
- No hardware execution or flashing performed as part of this work.

### Unchanged

- Ash-plate closing logic and endstop handling.
- Startup-failure detection and ignition retry behavior.
- Startup and runtime logos; previews extracted, replacement artwork pending.

### Firmware identifiers

| Image | SHA-256 |
| --- | --- |
| Original | `b5ab1b7380f2486c29cf6708954cdb5bbaa2d7798fd0103f845fa254da51a5e8` |
| Custom derivative | `b26b0b0177737d3884c2d4afb00cf03595c3f0b4c081e7d2dcc8388863f0a8ae` |

See [patch details](analysis/patched/README.md) for addresses, bytes, and reproduction instructions.
