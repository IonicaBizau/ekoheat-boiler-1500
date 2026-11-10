# Custom v2.42: dated Info label and no automatic idle clock

Built from the supplied original v1.73 according to [plan2.42.md](../../../plan2.42.md). The update package is [update-v2.42](../../../update-v2.42/), containing exactly `DTX9003.uc3` and the original v1.73 `license.key`. Copy the firmware first and the license second to the USB root. See [the update procedure](../../../docs/updating-firmware.md) for controller steps and settings checks.

The expected Info label is **`v2.42  Nov  8 2026`** (8 November 2026). The automatic inactivity path keeps the display active. Original v1.73 motor timing, three normal startup attempts, and special startup behavior are preserved. This build does not include the motor/startup changes in v2.73. The separate communication version fields still report the original vendor version; the custom revision is the Info label.

## How this differs from earlier patches

The patching method is the same one used for the current v2.73 image: check the original source hash, replace bytes in place, recalculate the payload CRC32, and keep the supplied license unchanged. The idle-clock instruction is identical to the v2.73 patch. Both builds put the full Info label directly into the existing string storage. An **earlier** v2.73 build changed a numeric version argument instead; that approach was later replaced after the reported mismatch between clock behavior and the Info display.

v2.42 makes fewer firmware changes than v2.73. It does not carry over the ash-plate timing and ignition-attempt changes. Its additional independent verifier and two-file update folder make the output easier to inspect and copy correctly. These checks do not establish why a previous update appeared to disappear or whether v2.42 will persist after a restart.

## Build and verify

Run from the repository root:

```sh
python3 analysis/tools/patch_v242.py
python3 analysis/tools/verify_v242.py --update-dir update-v2.42 --strict-package
```

The generator writes the image, supplied license and manifest here, independently verifies them, then copies only the two update files into `update-v2.42/`. It refuses unexpected entries in an existing update folder. The verifier uses fixed source hashes and patch expectations independently of the generator and manifest. Checks stay active under `python3 -O`.

For a FAT32 drive prepared on a Mac, verify the two required files even if macOS has added hidden metadata entries. The report lists any extra entries; the actual update package remains exactly two files.

```sh
python3 analysis/tools/verify_v242.py --update-dir /Volumes/USB_NAME
```

## Exact changes and identity

| Change | Virtual address | File offset | Replacement |
| --- | --- | --- | --- |
| Info format/date allocation | `0x80015130` | `0xD149` | 28 bytes: `v2.42  Nov  8 2026`, NUL terminated and padded |
| Idle expiry | `0x8000BA8E` | `0x3AA7` | `30 08` → `36 48`: `MOV R8,0` → `MOV R8,100` |
| Payload CRC32 | Wrapper | `0x15` | `A6 9E A7 CF` → `00 D4 DF 84` |

Image size is **453229 bytes**. Exactly **32 bytes** differ; all differences lie within these three ranges. Every other byte, including the 21-byte wrapper prefix and original control routines, matches stock v1.73.

| File | SHA-256 |
| --- | --- |
| Original v1.73 | `e57bb9517c66e8f37ecb864daca5735bc14e3ef6a2614c94a962dc62809f2e3a` |
| Custom v2.42 | `816adffec4f7427acdbc96a06916aac5d324ebbd8e08030205d21b79f4383185` |
| Supplied license (`34 1C`) | `8075e4bc145fadd645f7edfe2ec00c0b644b5a6edef3349531d5ff4cc155c3b5` |

The [manifest](DTX9003.json) records every changed offset. The [verification report](verification.json) checks original/output hashes, CRC32, exact allowed substitutions, the Info call and pointers, unchanged control routines, and the update copy. [Verifier checks](verifier-checks.json) also confirmed rejection of a modified source, unauthorized payload/date edits with recalculated CRCs, wrong license, stale USB image, extra package file, and an altered manifest. Those checks used temporary copies.

## Independent native inspection

Ghidra 12.2 AVR32-A SLEIGH disassembly of the original and output confirms only the idle `MOV` changes in the timer excerpt; the following `ST.H R9[0],R8` remains original, with RAM destination `0x2336`. See [original](idle-expiry-original.tsv) and [patched](idle-expiry-patched.tsv) instructions. The timer still expires and executes all its other work. Native [timer decompilation](decompiled/8000b410.txt) differs from the original C output only in assigning 100 instead of 0 to this request (apart from the input path in the tool transcript).

The [original](info-call-original.tsv) and [patched](info-call-patched.tsv) Info-call instructions are identical. They retain the format pointer `0x80015130`, destination `0x545C`, 33-byte limit and stack cleanup. The literal contains no format conversions, so the old numeric/date arguments are unused. Native [Info routine decompilation](decompiled/80015bf8.txt) has unchanged C output. Text is data, so it is verified as bytes rather than disassembled as code. The 18 visible characters plus NUL fit the destination.

Reproduce the native checks with the [analysis tooling](../../README.md). For example, set `SLA` to the installed `avr32a.sla` path, then run:

```sh
analysis/tools/avr32_dump "$SLA" analysis/patched/v2.42/DTX9003.uc3 0x80007fe7 0x8000ba3a 0x8000ba98
analysis/tools/avr32_dump "$SLA" analysis/patched/v2.42/DTX9003.uc3 0x80007fe7 0x80016776 0x80016794
```

The underlying behavior is supported by the original [timer](../../v1.73/decompiled/8000b410.txt), [backlight](../../v1.73/decompiled/80008348.txt), and [GUI](../../v1.73/decompiled/8001ed84.txt) routines. Explicit GUI/service transitions can still select the clock or alter brightness; this patch addresses the automatic inactivity path.

## Acceptance and persistence

Offline validation passed. A later controller attempt reportedly showed **1.73 immediately after the update sequence** and restored the idle clock after about four minutes; the v2.42 label was never seen. This does not establish that the patched image was installed. The supplied license is unchanged; its acceptance algorithm is unknown. There is no established license modification that fixes acceptance or persistence, and CRC32 validation cannot establish bootloader acceptance. See the [controller result](../../update-investigation.md#v242-controller-result--2026-11-09).

A subsequent attempt from successfully installed stock 1.72 also left Info at **1.72**. This rules out an already-installed 1.73 version as a sufficient explanation. The next useful check is whether the controller accepts the untouched stock 1.73 image and its original license from 1.72; see the [experiment result](../../update-investigation.md#result-of-the-172--v242-test).

After a successful update, record the exact Info label, remove USB as directed by the manual, verify the Ekoheat 1500 model/calibration/settings, and test inactivity and later normal restarts. If the label never changes, installation is unconfirmed. If it changes to v2.42 and subsequently reverts, record the sequence and investigate rollback/reflashing. See [the earlier investigation](../../update-investigation.md).

Copyright © Ekoheat for the underlying firmware, including the copy in `update-v2.42/`. See [third-party materials](../../../THIRD_PARTY.md).
