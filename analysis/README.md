# Working with the firmware

## Python-only workflows

Run from the repository root with Python 3.6 or later:

```sh
# v1.73 screen + 30-second opening allowance
python3 analysis/tools/patch_v173_30s.py
python3 analysis/tools/verify_patch.py --version 1.73

# v1.72 display + opening-allowance patch and boundary checks
python3 analysis/tools/patch_firmware.py
python3 analysis/tools/verify_patch.py

# Read original metadata and extract strings
python3 analysis/tools/inspect_firmware.py
```

These tools use only Python's standard library. The v1.72 asset extraction script, `analysis/tools/extract_bitmaps.py`, also uses only the standard library and writes the PNG/HTML previews in `analysis/assets/`.

You can recreate the patched `.uc3` files and manifests from the original images using the commands above. The scripts check the source hashes before patching. They do not flash a device. I have included the supplied `license.key` files with the firmware, but these tools do not need them.

## Native disassembly and decompilation

I keep the disassembly and decompiled routines under `ghidra/decompiled/`, `v1.73/decompiled/`, and the patch directories. Regenerating it requires additional tooling beyond Python:

- A Ghidra installation with AVR32-A big-endian SLEIGH support (`avr32a.sla`). The recorded analysis used Ghidra 12.2.
- A locally built native Ghidra decompiler at `analysis/ghidra/native-src/decomp_opt`.
- The C++ SLEIGH helper built from `analysis/tools/avr32_dump.cc`, if regenerating the TSV disassembly.

Native source, executables, and object files are excluded from Git. Obtain Ghidra from the [official upstream project](https://github.com/NationalSecurityAgency/ghidra), preserve its notices, and build against its matching source/API. The batch decompiler's historical default Ghidra path is machine-specific; override it with `--ghidra /path/to/ghidra`.

Generated XML images are also excluded. To recreate one for the original v1.73 image:

```sh
python3 - <<'PYCODE'
from pathlib import Path
b = Path("DTX9003 v1.73/DTX9003.uc3").read_bytes()
Path("analysis/v1.73/firmware.xml").write_text(
    '<binaryimage arch="avr32:BE:32:default:default">'
    '<bytechunk space="RAM" offset="0x80008000" readonly="true">'
    + b[25:].hex() + '</bytechunk></binaryimage>'
)
PYCODE
```

Then decompile a function into a fresh output directory (the batch script skips existing outputs):

```sh
python3 analysis/tools/decompile_functions.py   --ghidra /path/to/ghidra   --image analysis/v1.73/firmware.xml   --out analysis/v1.73/reproduced   0x8000b410
```

Address mapping for these images: `VA = file_offset + 0x80007FE7`. The first 25 file bytes are a wrapper; payload CRC32 is stored big-endian at offset `0x15` and covers offset `0x19` through EOF.

## Reading the evidence

- [Version comparison](v1.73/comparison.md): verified changes and remaining uncertainties.
- [Startup-failure analysis](startup-failure.md): detailed original v1.72 ignition paths.
- [v1.73 patch](patched/v2.73/README.md): screen and opening allowance.
- [v1.72 patch](patched/v1.72.42/README.md): display and opening-allowance changes.
- [Assets](assets/README.md): bitmap format and original UI placement.

Function matching files are heuristic aids. Address-normalized similarity does not establish semantic equivalence. Decompiled variable names are generated, and some calling-convention/varargs details remain unresolved.
