# Minimal v1.73 clock-screen patch

Output: `DTX9003_no_idle_clock.uc3`, derived from `DTX9003 v1.73/DTX9003.uc3`.
The source remains unchanged. Only two payload bytes change, plus the CRC32 field.

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

Static validation only: controller execution, bootloader acceptance and physical display behavior have not been tested.
