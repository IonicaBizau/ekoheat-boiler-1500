# Conditional 1.72 → v2.42 update experiment

The purpose is to test whether the controller refuses v2.42 while it already runs 1.73 because the patched image still carries original 1.73 version values outside its literal Info label. That is a **hypothesis**, not an established updater rule. A failure at any stage may still be caused by image/license checks or another updater rule. This experiment is not needed for normal boiler operation.

## Before deciding to run it

- The original 1.72 and 1.73 image/license pairs in this repository pass their stored payload CRC32 checks. That proves file integrity, **not** acceptance by this controller. The original 1.73 pair is the intended restoration material; no controller-specific recovery path has been verified. If there is no reliable way to restore 1.73 should the patched upgrade fail, do not run the experiment.
- Record the current Info version, Controller ID, boiler model, pellet calibration, and all settings. The [manual-based update guide](updating-firmware.md) warns that updates can reset settings and select Ekoheat 900. Finish the boiler's normal shutdown before any update. Keep stable power during updates and leave the boiler stopped between the two update stages.
- Use one image and **its own** `license.key` on the USB drive at a time. Clear the previous pair before copying the next pair. The controller has shown an update sequence without installing v2.42, so the sequence and touchscreen recalibration alone are not proof of success.

## File identity and checkpoints

| Stage | Copy these two files to the USB root | Expected SHA-256 of `DTX9003.uc3` | Info check immediately after update |
| --- | --- | --- | --- |
| 1: stock downgrade | `DTX9003 v1.72/DTX9003.uc3` + `DTX9003 v1.72/license.key` | `b5ab1b7380f2486c29cf6708954cdb5bbaa2d7798fd0103f845fa254da51a5e8` | 1.72 |
| 2: minimal custom upgrade | `update-v2.42/DTX9003.uc3` + `update-v2.42/license.key` | `816adffec4f7427acdbc96a06916aac5d324ebbd8e08030205d21b79f4383185` | `v2.42  Nov  8 2026` |
| Restoration material: stock 1.73 | `DTX9003 v1.73/DTX9003.uc3` + `DTX9003 v1.73/license.key` | `e57bb9517c66e8f37ecb864daca5735bc14e3ef6a2614c94a962dc62809f2e3a` | 1.73 |

Copy the firmware first, then its matching license, following the [existing update procedure](updating-firmware.md). Each USB preparation should contain the selected pair and no other firmware image. On a Mac, compare the file hashes on the **mounted USB volume**, not only in the repository. For stage 2, the repository verifier checks both files:

```sh
python3 analysis/tools/verify_v242.py --update-dir "/Volumes/YOUR_USB_NAME"
```

For stock stages, compare `shasum -a 256 "/Volumes/YOUR_USB_NAME/DTX9003.uc3"` with the table above, and compare the USB license with its source using `cmp`:

```sh
cmp "DTX9003 v1.72/license.key" "/Volumes/YOUR_USB_NAME/license.key"
# For a later stock 1.73 restoration, compare with DTX9003 v1.73/license.key instead.
```

**Stop after stage 1 if Info does not show 1.72.** If it does, prepare stage 2 from the v2.42 pair and check Info again immediately. If Info stays at 1.72, v2.42 was not demonstrated running; do not assume another attempt will help. To return to the prior 1.73 configuration, use the stock 1.73 pair as restoration material, while recognizing that its acceptance on this controller is unverified. If Info shows v2.42, remove the USB as directed, verify the Ekoheat 1500 model/calibration/settings, wait longer than the observed four-minute idle interval, and recheck after normal restarts.

If stage 2 works, that supports a same-version policy as one explanation for the original failure; it does not establish the full updater rule. If stage 2 fails, the result remains compatible with image/license rejection or another cause. In either case, preserve the exact Info values and update messages from each stage. Original v1.72 has different pump and input behavior from v1.73; see the [version comparison](../analysis/v1.73/comparison.md). Do not operate the boiler on an unverified configuration.

## Observed result and next check

The user reports that stage 1 installed and Info showed 1.72, then stage 2 left Info at 1.72. A same-version gate alone therefore does not explain the patched-image failure. The next check is to install the **untouched stock 1.73 pair** in the restoration row and confirm whether Info changes to 1.73. Verify both files on the USB first, and recheck the boiler model, calibration, and settings afterward. This result will distinguish a problem specific to the modified package from a broader inability to move from 1.72 to 1.73; it will not reveal the exact acceptance rule.
