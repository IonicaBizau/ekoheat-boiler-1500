# Updating the boiler software

I keep the update steps here so I do not have to hunt through the manual each time. The USB procedure comes from the [2014 English manual, page 16](ekopower%20ekoheat%20installation%20manual%202%202014%20eng.pdf#page=16); the [series manual, PDF page 36 / printed page 32](ekoheat_series.pdf#page=36) also describes updating through USB and reserves it for authorised personnel.

The v2.42 files pass offline checks, but a reported controller update attempt did not show the v2.42 label or clock behavior. Actual installation, bootloader acceptance, license handling, and physical operation with these patches remain unverified. The steps below describe the vendor's update process, with this project's files substituted.

## Before updating

Stop the boiler through its normal shutdown process and let it finish. Record the current software version, controller ID, boiler model, pellet calibration, and your settings before starting. Keep the original firmware and its matching `license.key` available separately. Having the original files does not establish a recovery method if an update fails.

The manual warns that updating can reset **all settings** and select **Ekoheat 900**. My boiler is an **Ekoheat 1500**, so checking the model and restoring the pellet calibration afterwards matters.

Check which controller and manual match your boiler. The USB port may be accessible behind the rubber plug on newer controllers; older units require opening the controller housing. Have a qualified technician handle internal access, with mains power isolated before opening. Do not work inside a powered controller. Keep power stable during the actual software update.

## Pick the files

Use one firmware image and the license file supplied with its source version:

| Custom version | Patched image in this repository | Matching license file |
| --- | --- | --- |
| **2.42** (minimal v1.73 patch) | [`update-v2.42/DTX9003.uc3`](../update-v2.42/DTX9003.uc3) | [`update-v2.42/license.key`](../update-v2.42/license.key) |
| **1.73, clock disabled** | [`update-v1.73-no-clock/DTX9003.uc3`](../update-v1.73-no-clock/DTX9003.uc3) | [`update-v1.73-no-clock/license.key`](../update-v1.73-no-clock/license.key) |
| **1.72, clock disabled** | [`update-v1.72-no-clock/DTX9003.uc3`](../update-v1.72-no-clock/DTX9003.uc3) | [`update-v1.72-no-clock/license.key`](../update-v1.72-no-clock/license.key) |
| **1.72.42** | [`analysis/patched/v1.72.42/DTX9003.uc3`](../analysis/patched/v1.72.42/DTX9003.uc3) | [`analysis/patched/v1.72.42/license.key`](../analysis/patched/v1.72.42/license.key) |
| **2.73** | [`analysis/patched/v2.73/DTX9003.uc3`](../analysis/patched/v2.73/DTX9003.uc3) | [`analysis/patched/v2.73/license.key`](../analysis/patched/v2.73/license.key) |

**v2.42** keeps the current screen awake and displays `v2.42  Nov  8 2026`. It preserves original v1.73 ash-plate timing and three normal startup attempts. The [update-v2.42 folder](../update-v2.42/) contains only the two files needed for USB; analysis and verification records are [stored separately](../analysis/patched/v2.42/README.md).

The [clock-only v1.73 folder](../update-v1.73-no-clock/) changes only the automatic idle-clock instruction and required CRC32. It keeps the original 1.73 Info label, date, communication version, and license. To verify its copy on the USB drive, run `python3 analysis/tools/verify_v173_no_clock.py --update-dir "/Volumes/YOUR_USB_NAME"` from the repository root. Because its Info label is unchanged, a 1.73 display alone cannot prove installation; check the idle behavior after the observed four-minute interval. Its acceptance on the controller is unverified.

The [clock-only v1.72 folder](../update-v1.72-no-clock/) likewise keeps the original 1.72 version, date, and license. Verify its USB copy with `python3 analysis/tools/verify_v172_no_clock.py --update-dir "/Volumes/YOUR_USB_NAME"`. Since the controller already shows 1.72, a 1.72 Info display cannot establish whether this patch installed. The previous clock-only v1.73 package reportedly did not load; the acceptance rule remains unknown.

A subsequent clock-only v1.72 attempt left the idle clock appearing, so the intended behavior was not observed. No further modified package has a demonstrated acceptance path on this controller; see the [investigation](../analysis/update-investigation.md).

The older v1.72.42 and v2.73 custom builds keep the screen awake and allow the ash plate **30 seconds beyond the configured opening time**. The v2.73 rebuild additionally allows five total normal startup attempts; v1.72.42 retains three. Longer ignition operation has not been validated on hardware. The version numbers identify these custom patches; they are not official vendor releases.

To regenerate and check the combined images, run these commands from the repository root:

```sh
# v2.42, including its two-file update folder
python3 analysis/tools/patch_v242.py
python3 analysis/tools/verify_v242.py --update-dir update-v2.42 --strict-package

# v1.72.42
python3 analysis/tools/patch_firmware.py
python3 analysis/tools/verify_patch.py

# v2.73
python3 analysis/tools/patch_v173_30s.py
python3 analysis/tools/verify_patch.py --version 1.73
```

These commands write files locally; they do not flash the boiler. See the [v1.72 patch notes](../analysis/patched/v1.72.42/README.md) and [v1.73 patch notes](../analysis/patched/v2.73/README.md) for hashes, checksums, and validation limits. Using the supplied license file with its corresponding version follows the original packaging; it is not a tested guarantee of acceptance on your controller.

## Prepare the USB drive

1. Use an empty USB flash drive. Back up anything on it before clearing it.
2. Copy the chosen patched `.uc3` file to the drive's root and keep its name as **`DTX9003.uc3`**. Leave the original file in the repository as it is.
3. Then copy the matching **`license.key`** to the drive's root. Copy it as a file; do not open and re-save it in a text editor. These supplied files contain nonprinting bytes.
4. Check that the drive contains the two files below, rather than a ZIP archive, a containing folder, or a file ending in `.uc3.uc3`. Eject the drive cleanly.

```text
USB drive/
├── DTX9003.uc3
└── license.key
```

Each patched folder already includes the matching `license.key`, so both USB files can be taken from the same folder.

After copying v2.42, compare the two required USB files with the verified build (replace the drive path). On a Mac-prepared FAT32 drive, macOS may add hidden metadata entries; this check lists those entries without treating them as a firmware or license mismatch:

```sh
python3 analysis/tools/verify_v242.py --update-dir /Volumes/USB_NAME
```

For the older v2.73 build instead:

```sh
python3 analysis/tools/verify_patch.py --version 1.73 --update-dir /Volumes/USB_NAME
```

This detects copied-file mismatches; it does not prove controller acceptance. See the [update investigation](../analysis/update-investigation.md) for the reported v2.73 failure and checks performed.

The manual specifies copying the firmware first and the license file second. It does not specify a filesystem format or USB capacity, so I have not assumed a particular one here.

## Run the update

1. With safe access to the controller's USB port arranged, insert the prepared drive.
2. In the 2014 manual's interface, open **Menu → Fitters settings → Next**, then select **Download** beside **New software**. Confirm the download prompt. Other controller layouts may use different labels; the series manual lists **New software** in its technical settings menu.
3. Let the update finish without removing the drive or interrupting power. The 2014 manual describes a black screen for roughly **15–20 seconds**, followed by the EKOPOWER logo and a countdown from five. That is the manual's expected sequence, not a measured time for these patches.
4. After that sequence completes, remove the USB drive and have any opened housing safely reassembled before normal use.

If the controller rejects the files or does not return to its normal interface, do not assume the update succeeded or repeatedly power-cycle it. Record what happened and consult the controller's service support; this project has no verified bootloader recovery procedure.

## Check before restarting the boiler

Open **Info** and check the software label. For **v2.42**, expect **`v2.42  Nov  8 2026`**. The older v2.73 label reads `v2.73  Nov  1 2026`; v1.72.42 retains its original vendor build date. The physical label layout has not been checked on the display.

For v2.42, check Info immediately after the update countdown, then leave the screen untouched for **longer than the controller's observed roughly four-minute inactivity interval** to check the clock behavior. Repeat after USB removal and later normal power cycles. The source-matched license is unchanged, and no license modification has been shown to fix acceptance or persistence. A reported attempt showed 1.73 immediately and the clock after about four minutes; the [investigation](../analysis/update-investigation.md#v242-controller-result--2026-11-09) records what remains to be checked.

Verify the boiler model is **Ekoheat 1500**, then compare all settings with your record and restore the pellet calibration if it was reset. The 2014 manual describes selecting the boiler size under **Menu → Self test**; use the model-selection instructions that match your controller, and avoid activating unrelated test outputs.

Only resume normal operation after the model, calibration, settings, and any faults have been checked. The label alone does not prove that the motor timing or other physical behavior works correctly.
