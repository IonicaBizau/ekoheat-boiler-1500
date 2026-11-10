# v2.73 update investigation

The user reported that the update did not load, with similar behavior previously seen on another USB drive. This time it occurred with a drive that had worked before. No specific rejection message or currently running version was provided. No firmware change is justified as an update fix from this report alone.

## Rechecked files

- v2.73 is 453229 bytes, the same length as the supplied v1.73 image.
- The 21-byte wrapper prefix is unchanged. Its `AVR32` signature is intact.
- Stored big-endian payload CRC32 is `0465D03D` for the dated literal-label rebuild, matching the CRC32 of bytes from offset 25 through EOF.
- The supplied license remains byte-for-byte identical to the v1.73 source (`34 1C`). Its validation algorithm is unknown; matching the supplied license does not prove acceptance of modified firmware.
- Exactly 41 bytes differ from the source, restricted to CRC32, idle expiry, opening allowance, Info label storage, and two startup instructions. See the current manifest for offsets.
- The Info label is now the literal `v2.73  Nov  1 2026`, inside the original 28-byte format/date region. Numeric arguments are original and unused by this literal. This check does not establish whether the updater has any additional version policy.
- Original source hashes, generated output hash, instruction checks, and 326777 opening-time comparisons pass.

The supplied application payload starts at `0x80008000`; it does not include the lower flash region. No updater acceptance algorithm has been established from this application analysis. Do not infer a signature requirement, license fix, or version rejection from the failure report alone.

`verify_patch.py` now checks the wrapper and supplied license explicitly and accepts `--update-dir` to compare both USB files byte-for-byte against the verified build. It reads the USB files without changing them:

```sh
python3 analysis/tools/verify_patch.py --version 1.73 --update-dir /Volumes/USB_NAME
```

## Startup attempts

The original v1.73 state machine at `0x80024100` uses an 8-bit counter at RAM `0x2365`. It increments after the configured ignition wait and retries while the new count is below 3. Machine instructions at `0x80024440` through `0x80024446` compare that count with 2 and branch to the failure assignment if it is higher. Thus normal startup has three attempts.

There is also a separate fuel-charge gate: the entry code only recalculates charging while the count is below 2 (`0x80024288` through `0x8002428E`). The first charge uses the initial quantity, and the second uses a quarter-based calculation. The third bypasses that charging setup. Increasing the retry comparison alone does not define a new fuel-charge sequence.

The ignition routine at `0x8000ED44` additionally seeds the counter to 3 on the `0x22F3 == 2` path. Raising the limit could change this path as well as normal startup. It also keeps the ignition request active until light detection, so a higher retry limit can extend ignition operation. The separate startup-ramp low-light failure remains a different cause of “Startup failed!” and would not be fixed by extra attempts.

The user requested five total attempts. The rebuild changes the limit comparison to 4 and the special-path exhausted seed to 5, retaining that path's first-timeout failure. Charging conditions are unchanged. Independent native decompilation confirms both edits; the verifier checks five failed waits and unchanged remaining routine bytes. Physical ignition duty limits remain unverified. The earlier three-attempt v2.73 had CRC32 `DD3E71AC`; the rebuilt image has CRC32 `3DA58A4D`. This startup change is not claimed to fix USB loading. Evidence: [state machine](v1.73/decompiled/80024100.txt), [ignition routine](v1.73/decompiled/8000ed44.txt), and [original startup-failure analysis](startup-failure.md).

## Info label follow-up

The user subsequently reported no idle clock and `1.73` on the Info screen. The installed file's identity remains unconfirmed. The prior numeric-argument patch still statically predicts `2.73`; no cause of the mismatch has been proven. The current rebuild embeds the complete label literally in the Info formatter's storage. Its CRC32 is `0465D03D`; the preceding five-attempt build's CRC32 was `3DA58A4D`. This removes numeric formatting as a factor without changing the clock or startup patches. Hardware display and acceptance of this latest rebuild remain untested.

The current literal label uses the custom build date November 1, 2026, at the user's request. The vendor source date remains July 13, 2016; the source file is untouched.

## Later v2.42 derivative

The [v2.42 build](patched/v2.42/README.md) applies the same idle instruction and literal-label method to the original v1.73 firmware, with the requested November 8, 2026 date. It omits the v2.73 ash-plate and ignition changes and uses a stricter independent byte/package verifier. This changes the patch scope and verification, not the controller's unknown update or license rules. The earlier reported load failure and `1.73` Info display remain unexplained until an exact installed image is identified and checked after normal restarts.

## v2.42 controller result — 2026-11-09

The user reports copying and replacing both files from `update-v2.42/`, seeing the controller's update sequence and a touchscreen recalibration prompt, then seeing `1.73` in Info immediately afterward. The clock returned after about four minutes. The custom label was never observed. Thus neither intended v2.42 behavior was demonstrated on the controller; the update sequence and recalibration alone do not identify the code that ran. This is evidence against a simple *later* rollback after initially running v2.42. The controller's flash contents cannot be read here.

The next discriminating check was to compare the two files actually used on the USB drive against `update-v2.42/` with `python3 analysis/tools/verify_v242.py --update-dir /Volumes/USB_NAME`; the result appears below. If they match, investigate update acceptance, version policy, and license handling with controller/service evidence before changing bytes. The current application payload does not include the bootloader, so no acceptance or license algorithm has been established. Do not treat a recalibration prompt as proof that the patched application was installed.

The user reports preparing the USB drive on a Mac with FAT32. The supplied manual does not specify a filesystem format. macOS can add hidden metadata entries to a removable drive, so the USB verifier now compares the two required file contents while listing additional entries. The project package itself still must contain exactly the two intended files. No evidence currently links FAT32 or metadata entries to the controller's unchanged 1.73 behavior.

### USB read-back result

The user ran the updated verifier against the mounted `/Volumes/8 GB` drive. It reported **PASS**: `DTX9003.uc3` is 453229 bytes with SHA-256 `816adffec4f7427acdbc96a06916aac5d324ebbd8e08030205d21b79f4383185`; `license.key` is the two-byte original v1.73 key with SHA-256 `8075e4bc145fadd645f7edfe2ec00c0b644b5a6edef3349531d5ff4cc155c3b5`. The only extra root entries reported were `.Spotlight-V100`, `.fseventsd`, and `System Volume Information`. A separate read in this workspace confirmed the same two hashes on that mounted drive. File-copy mismatch is therefore ruled out for the drive as read back; whether the controller accepted the image remains unknown.

The mounted volume reports `msdos` (`/dev/disk8s1`), consistent with the user's FAT32 preparation. The user recalls no warning or error message during the update sequence. Neither point proves application installation, since Info stayed at 1.73 and the idle clock returned.

The v2.42 edits change a UI string and the idle timer instruction. Other application version bytes remain at the original 1.73 values, and the wrapper prefix is unchanged. A same-version update policy or an image/license integrity check could explain a skipped installation, but neither mechanism has been demonstrated in the available application image. The bootloader and its acceptance rules are absent. Do not issue another firmware build or alter `license.key` on either hypothesis alone.

### Next evidence to obtain

The user reports that the company previously suggested as a service contact no longer exists. The investigation therefore does not depend on vendor support. The supplied manuals document the USB file order and controller sequence, but do not document updater acceptance checks or a flash read-back command. The repository has application images only; no bootloader or full flash dump is available.

The manuals say the ordinary **Info** display includes software version, **Controller ID / Control card ID**, and selected boiler model. Record these without entering a configuration or service menu; the ID may help identify the controller, although it does not reveal the updater's rules by itself. The next technical evidence is a **read-only controller flash dump** or a known full-chip image for the same controller revision. If a qualified electronics technician can obtain a dump without changing flash, compare the installed application region beginning at `0x80008000` with the original v1.73 and patched v2.42 payloads, then inspect the lower flash region for USB image, version and license checks. Preserve the dump and its SHA-256 before analysis. Do not assume an AVR32 debug connector, pinout or procedure without identifying the board.

The user has supplied the Controller ID from Info. It is a serial identifier, not an established board model or revision; the full number is omitted from this repository. Its ASCII and 32-bit big-/little-endian representations were not found as literal bytes in either original firmware image. A historical [Ekoheat brochure](https://www.nhbioservice.dk/wp-content/uploads/2015/05/ekoheat900.pdf) describes updates in relation to the controller/boiler serial number. That wording raises the possibility of serial-specific update selection, but does not establish that `license.key` is tied to this ID or reveal the updater's validation method. No public lookup for this exact ID or matching bootloader documentation was found.

The user later read a board marking `DTX90003` and an Atmel chip marked `32UC3A0512-U`, with lower line `1114 D5KQ 1`. The chip marking identifies the [AT32UC3A0512 family](https://www.microchip.com/en-us/product/at32uc3a0512), whose [datasheet](https://www.microchip.com/content/dam/mchp/documents/OTH/ProductDocuments/DataSheets/doc32058.pdf) specifies 512 KiB embedded flash mapped at `0x80000000` and JTAG capability. This fits the firmware's AVR32 architecture and its application address `0x80008000`. The address leaves 32 KiB below the application, but does not establish this board's actual bootloader contents, protection fuses, or update algorithm. The same datasheet describes a security bit that can block external debug readout; clearing it requires a chip erase, so any attempted readout must avoid erase or programming operations. The lower chip line has not been decoded here.

If a read-back is unavailable, look for a documented updater diagnostic or status path specific to this controller. The current files and observed UI behavior cannot distinguish a same-version skip from an image/license integrity rejection. Neither rewriting `license.key` nor changing additional firmware version bytes is justified yet.

### Offline wrapper and license comparison

Both original images have the same 21-byte wrapper prefix: ASCII `AVR32` followed by 16 bytes that can be displayed as UUID `a321b420-3ee9-11dd-ae16-0800200c9a66`. Their differing four-byte fields at offset `0x15` are the verified payload CRC32 values. There is no evident release-version field in this wrapper prefix. The supplied `license.key` values are `29 0A` for v1.72 and `34 1C` for v1.73. Neither equals the low 16 bits of its payload CRC32, the low 16 bits of the whole-file CRC32, nor a CRC-CCITT (`crc_hqx`, initial value 0 or `0xFFFF`) over the payload or whole file. These checks rule out only those simple formulas; two samples cannot establish the key algorithm. Searching the wrapper UUID and file name did not locate a public updater-format specification.

### Downgrade to v1.72 as a test

Do not treat a v1.72 downgrade followed by v2.42 as the next diagnostic step. It might test a same-version gate only if the controller accepts the downgrade and then accepts a modified 1.73 image; a license or image integrity check would still reject v2.42. The downgrade itself changes controller behavior, including pump control and digital-input handling documented in the [v1.72/v1.73 comparison](v1.73/comparison.md), and the manual warns that updates may reset settings and select Ekoheat 900. There is no verified recovery path for a failed downgrade. Obtain acceptance or read-back evidence first.

The user later clarified **v1.71**, not v1.72. No v1.71 image or matching license exists in this repository, and its control behavior has not been compared with v1.73. If the user has a previously working, authentic v1.71 package, that may reduce uncertainty about the downgrade file itself, but it still cannot distinguish a same-version gate from a payload/license rejection of v2.42 if the second step fails. A downgrade/upgrade sequence is therefore a hardware experiment with a real intermediate firmware state and an unverified route back to v1.73, rather than an established fix.

The user corrected the version again to **v1.72** and intends to test original 1.72 followed by v2.42. Both original 1.72 and 1.73 file pairs have valid payload CRC32 values. The [conditional experiment guide](../docs/v172-to-v242-experiment.md) records the exact files, hashes, stop conditions, and the unverified restoration risk. No controller update has been performed as part of preparing that guide.

### Result of the 1.72 → v2.42 test

The user reports that original 1.72 installed successfully, but after the v2.42 update attempt Info still showed 1.72. This rules out *being on 1.73 already* as a sufficient explanation for the earlier failed v2.42 attempt. It does not identify the actual rejection rule or prove whether the controller read the patched file. In particular, the stock 1.72 installation does not validate the unchanged v1.73 license against a modified v1.73 image.

The next practical diagnostic and intended restoration is the untouched original v1.73 image **with its original v1.73 `license.key`**. Verify the copied pair on the USB drive, perform the documented update, and check Info. If stock 1.73 installs from the same 1.72 state, the modified v2.42 package is the distinguishing factor; possible checks include an unknown image signature or license binding, but neither is established. If stock 1.73 also leaves Info at 1.72, investigate the update procedure, USB readback, and controller acceptance/status path before trying any further custom image. Do not derive or alter a key from these outcomes alone.

The user later reports that a clock-only derivative of stock v1.73 also did not load. A new [clock-only stock v1.72 package](patched/v1.72-no-clock/README.md) was prepared at the user's request. It retains all v1.72 version bytes and its original license; only the idle instruction and CRC32 differ. This is an offline build, not evidence that modified packages are accepted. If the controller remains on 1.72 after a future attempt, the unchanged Info version alone cannot identify whether the image ran.

After attempting the clock-only v1.72 package, the user reports no complaint or error and no touchscreen recalibration, but is unsure whether installation occurred. Those observations are inconclusive: the update manual does not identify recalibration as a required stage, and both stock and modified images display 1.72. The next observable check is to leave the same screen untouched beyond the previously observed four-minute clock interval, then repeat after a normal restart with the USB removed. The clock behavior provides evidence about the intended patch, though a read-back would be needed to identify the exact installed bytes.

The user then observed that the clock **did appear**. Thus the desired change was not active in this test. The unchanged 1.72 Info label cannot distinguish a rejected/skipped image from an installed image whose idle-clock path differs from the static prediction. Do not treat the package's offline PASS result as an installation result. The most useful next controlled comparison remains untouched stock 1.73 plus its original license from the current 1.72 state, followed by Info and settings checks; this tests whether a stock upgrade is accepted while modified packages are not.

The user reports that this untouched stock 1.73 update also failed. A read-only check of the currently mounted `/Volumes/8 GB` drive found the exact stock v1.73 firmware (`e57bb9517c66e8f37ecb864daca5735bc14e3ef6a2614c94a962dc62809f2e3a`) and matching license (`8075e4bc145fadd645f7edfe2ec00c0b644b5a6edef3349531d5ff4cc155c3b5`), plus two 4096-byte AppleDouble sidecars, `._DTX9003.uc3` and `._license.key`, and the directories `.Spotlight-V100`, `.fseventsd`, and `System Volume Information`. The sidecars start with the AppleDouble magic `00 05 16 07`. The mounted filesystem reports `msdos`. The extra entries could affect an updater that scans the root broadly, but no such behavior has been established. This stock-file failure shifts the next diagnostic toward the USB medium, root contents, partition format, or update procedure rather than a modified-image-only rejection.
