# Plan for custom v2.42 firmware (8 November 2026)

## Goal and starting point

Create a reproducible, minimal derivative of the **original v1.73** `DTX9003.uc3` that shows `v2.42  Nov  8 2026` in Info and keeps the current screen visible when the inactivity timer expires. Treat `2.42` as a custom display label, not an official vendor version. Leave ignition attempts, ash-plate timing, and other control behavior at the original v1.73 settings. The existing v2.73 image includes those extra changes and is not the base for this build.

The reported earlier result was that the idle clock stayed away while Info showed `1.73`; an update was also reported as failing to load. Those observations do **not** establish that a successfully installed image was later erased. Establish what is actually installed before diagnosing persistence. See [the update investigation](analysis/update-investigation.md).

## Changes to make

1. Add a dedicated generator for `analysis/patched/v2.42/DTX9003.uc3`, using `analysis/tools/patch_firmware.py` for source-hash checking, same-length substitutions, payload CRC32 recalculation, and a manifest. Require the original v1.73 SHA-256 `e57bb9517c66e8f37ecb864daca5735bc14e3ef6a2614c94a962dc62809f2e3a`. Never use a previously patched image as input.
2. At virtual address `0x80015130` (file offset `0xD149`), replace the original 28-byte Info format/date allocation with the NUL-terminated literal `v2.42  Nov  8 2026`, padded with NUL bytes to exactly 28 bytes. This follows the current v2.73 literal-label approach. Verify that the Info call still points to this string and its original destination and that the displayed text fits its 33-byte destination buffer. The former numeric version arguments and date pointer become unused; do not change their instructions merely to alter the label.
3. At `0x8000BA8E` (file offset `0x3AA7`), change `30 08` to `36 48`, the same two-byte idle-expiry substitution used by v2.73. It changes the brightness request written on inactivity expiry from 0 to 100, preventing the observed automatic path to the clock. Confirm by disassembly that the store destination and surrounding timer logic are unchanged. This does not remove every possible explicit clock or brightness transition.
4. Keep the 21-byte wrapper prefix, image length, all other payload bytes, and the source firmware untouched. Recompute only the four-byte CRC32 at file offsets `0x15`–`0x18` after the two substitutions. Copy the original v1.73 `license.key` byte-for-byte into the new output folder; record its hash. Do not invent a modified key.

## Checks before preparing a USB drive

- Extend or add a verifier for **v2.42 specifically**. Check source/output hashes, wrapper, payload CRC32, exact changed-byte allowlist, original and patched instruction bytes, literal text/NUL padding, Info format and destination pointers, and unchanged startup and ash-plate routines. Re-disassemble the two edited locations independently of the generator.
- Produce the manifest, verification report, and short patch notes under `analysis/patched/v2.42/`. Document the exact output SHA-256 and CRC32 so the image used on the USB drive can be identified later. Compare both copied USB files byte-for-byte with the verified image and supplied key.
- Update `docs/updating-firmware.md` only after the v2.42 artifact and verifier exist. Preserve the vendor filename `DTX9003.uc3` at the USB root and use the source-matched `license.key` as described in the existing guide. Record current controller ID, Info label, model, pellet calibration, and settings before updating.

## License and persistence investigation

The supplied v1.73 key is only **two bytes** (`34 1C`); the existing v2.73 package copies it unchanged. The repository has no proven updater/bootloader validation algorithm, and the application image does not contain the lower flash region. Therefore there is currently **no evidence that changing `license.key` is necessary or would make an update persistent**. Changing it by guesswork could instead prevent acceptance. Use the unmodified source-matched key for the first controlled attempt.

To distinguish rejection, rollback, and a display mismatch, record the controller's exact update messages and full power-on sequence. Check the Info label and clock behavior immediately after the update, after USB removal, after a normal power cycle, and after a later power cycle. Photograph or transcribe the same Info screen each time. Record whether settings reset or the controller selects Ekoheat 900. If Info remains `1.73` but the clock behavior changes, investigate whether the display uses another version path or whether an older image was installed. If `v2.42` appears and later returns to `1.73`, investigate a true rollback or reflash, including whether the USB drive was left connected. If the updater rejects the files, retain the exact error and ask service support about its license/version rules; do not infer a key algorithm from the two-byte sample.

## Release gate

Static checks can establish byte integrity and the intended control-flow change, but **cannot prove update acceptance, persistence, or safe operation on the boiler**. Flash only through the documented controller procedure with stable power and a known service/recovery path. After installation, confirm `v2.42  Nov  8 2026`, unchanged expected heating behavior, the Ekoheat 1500 model and settings, and no automatic idle clock. Repeat the version check after normal restarts before calling the update persistent. If the controller rejects the image, loses the label, or behaves unexpectedly, stop and diagnose that observation before making further firmware or license changes.
