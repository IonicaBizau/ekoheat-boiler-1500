# Stock 1.72 with the automatic idle clock disabled

The USB-ready folder is [`update-v1.72-no-clock/`](../../../update-v1.72-no-clock/). It contains exactly `DTX9003.uc3` and the original v1.72 `license.key`. All original v1.72 version and date bytes, motor control, startup logic, and other payload bytes are preserved except the idle instruction. **Info should still show 1.72 if this image installs.**

At virtual address `0x8000B964` (file offset `0x397D`), `30 08` (`MOV R8,0`) becomes `36 48` (`MOV R8,100`). The required payload CRC32 at wrapper offset `0x15` becomes `DB 18 B8 1D`, from `42 45 23 53`. The image remains 450509 bytes. This same idle instruction was used in the earlier combined v1.72 patch; the version-label, ash-plate, and other changes from that build are absent here. The change addresses the automatic inactivity path, not every explicit way to select the clock.

| File | SHA-256 |
| --- | --- |
| Stock v1.72 firmware | `b5ab1b7380f2486c29cf6708954cdb5bbaa2d7798fd0103f845fa254da51a5e8` |
| Clock-only v1.72 firmware | `25bd8691cfc0150dd1f20fb035154a5dcaa8fc666d08cb76633173584137fd02` |
| Original v1.72 license | `fafba0527c3953c4b6e0e5b5739ba83612f8053bcdc9466730193cd1d590b408` |

From the repository root, rebuild and verify:

```sh
python3 analysis/tools/patch_v172_no_clock.py
python3 analysis/tools/verify_v172_no_clock.py
```

After copying the pair to a mounted USB drive, verify the actual drive copy:

```sh
python3 analysis/tools/verify_v172_no_clock.py --update-dir "/Volumes/YOUR_USB_NAME"
```

The verifier reconstructs the output independently from hash-identified stock v1.72 and rejects any other modified byte, wrong license, or extra package file. A deliberately altered image was rejected. These offline checks do not establish controller acceptance. The user reports that the separate clock-only v1.73 package did not load; the reason remains unknown. Since Info remains 1.72 for both stock and this patch, only observed clock behavior or a read-back can distinguish them. See the [USB update guide](../../../docs/updating-firmware.md) and [investigation](../../update-investigation.md).

In the first controller attempt with this v1.72 package, the clock still appeared after inactivity. The intended change was therefore **not observed on hardware**. Whether the controller rejected the image or ran it without the expected effect remains unresolved.

The underlying firmware and supplied license remain the vendor's materials. See [third-party materials](../../../THIRD_PARTY.md).
