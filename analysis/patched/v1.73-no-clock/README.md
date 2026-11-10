# Stock 1.73 with the automatic idle clock disabled

The USB-ready folder is [`update-v1.73-no-clock/`](../../../update-v1.73-no-clock/). It contains only `DTX9003.uc3` and the original v1.73 `license.key`. The Info label, date, communication version bytes, motor control, and startup logic remain identical to stock 1.73. **Info should still show 1.73 if this image installs.**

Only the idle-expiry instruction at virtual address `0x8000BA8E` (file offset `0x3AA7`) changes from `30 08` (`MOV R8,0`) to `36 48` (`MOV R8,100`). The wrapper payload CRC32 at offset `0x15` changes from `A6 9E A7 CF` to `C0 97 A8 3F`. The image remains 453229 bytes. This uses the same idle instruction as the earlier v2.73 and v2.42 patches. It addresses the automatic inactivity path; explicit UI or service actions can still select the clock.

| File | SHA-256 |
| --- | --- |
| Stock v1.73 firmware | `e57bb9517c66e8f37ecb864daca5735bc14e3ef6a2614c94a962dc62809f2e3a` |
| Clock-only firmware | `dec5a6496a4688258a0566d9b33cdf61f9497d18912310e097b71bf91972503e` |
| Original v1.73 license | `8075e4bc145fadd645f7edfe2ec00c0b644b5a6edef3349531d5ff4cc155c3b5` |

From the repository root, rebuild and verify:

```sh
python3 analysis/tools/patch_v173_no_clock.py
python3 analysis/tools/verify_v173_no_clock.py
```

After copying the two files to a mounted USB drive, check the actual USB copy:

```sh
python3 analysis/tools/verify_v173_no_clock.py --update-dir "/Volumes/YOUR_USB_NAME"
```

The verifier reconstructs the exact image from hash-identified stock v1.73 and rejects any other changed bytes, wrong license, extra files in the package folder, or mismatched USB copies. It allows macOS metadata entries on the USB and lists them. The checks prove file integrity and the intended instruction substitution, not bootloader acceptance or physical execution. Previous attempts to install a different modified v1.73 image left the controller on its prior version; this clock-only image has not been tested on the controller. See the [update investigation](../../update-investigation.md) and [USB procedure](../../../docs/updating-firmware.md).

The underlying firmware and supplied license remain the vendor's materials. See [third-party materials](../../../THIRD_PARTY.md).
