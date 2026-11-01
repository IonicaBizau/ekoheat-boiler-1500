# v1.73: earlier screen-only patch

The earlier output below is still available and retains the original 10-second opening allowance.

Output: `DTX9003.uc3`, derived from `DTX9003 v1.73/DTX9003.uc3`.
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

The combined custom version is documented under [v1.73.42](../v1.73.42/README.md).
