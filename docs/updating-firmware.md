# Updating the boiler software

I keep the update steps here so I do not have to hunt through the manual each time. The USB procedure comes from the [2014 English manual, page 16](ekopower%20ekoheat%20installation%20manual%202%202014%20eng.pdf#page=16); the [series manual, PDF page 36 / printed page 32](ekoheat_series.pdf#page=36) also describes updating through USB and reserves it for authorised personnel.

**I have not flashed these patched images.** Their offline checks pass, but bootloader acceptance, the supplied license files, and physical operation with these patches have not been verified. The steps below describe the vendor's update process, with this project's files substituted.

## Before updating

Stop the boiler through its normal shutdown process and let it finish. Record the current software version, controller ID, boiler model, pellet calibration, and your settings before starting. Keep the original firmware and its matching `license.key` available separately. Having the original files does not establish a recovery method if an update fails.

The manual warns that updating can reset **all settings** and select **EkoHeat 900**. My boiler is an **EkoHeat 1500**, so checking the model and restoring the pellet calibration afterwards matters.

Check which controller and manual match your boiler. The USB port may be accessible behind the rubber plug on newer controllers; older units require opening the controller housing. Have a qualified technician handle internal access, with mains power isolated before opening. Do not work inside a powered controller. Keep power stable during the actual software update.

## Pick the files

Use one firmware image and the license file supplied with its source version:

| Custom version | Patched image in this repository | Matching license file |
| --- | --- | --- |
| **1.72.42** | [`analysis/patched/DTX9003_no_idle_clock_30s.uc3`](../analysis/patched/DTX9003_no_idle_clock_30s.uc3) | [`DTX9003 v1.72/license.key`](../DTX9003%20v1.72/license.key) |
| **1.73.42** | [`analysis/patched/v1.73/DTX9003_no_idle_clock_30s.uc3`](../analysis/patched/v1.73/DTX9003_no_idle_clock_30s.uc3) | [`DTX9003 v1.73/license.key`](../DTX9003%20v1.73/license.key) |

Both custom versions keep the current screen awake and allow the ash plate **30 seconds beyond the configured opening time**. The version numbers identify these custom patches; they are not official vendor releases. The earlier `DTX9003_no_idle_clock.uc3` image for v1.73 only changes the display behavior and retains the original version label and opening allowance.

To regenerate and check the combined images, run these commands from the repository root:

```sh
# v1.72.42
python3 analysis/tools/patch_firmware.py
python3 analysis/tools/verify_patch.py

# v1.73.42
python3 analysis/tools/patch_v173_30s.py
python3 analysis/tools/verify_patch.py --version 1.73
```

These commands write files locally; they do not flash the boiler. See the [v1.72 patch notes](../analysis/patched/README.md) and [v1.73 patch notes](../analysis/patched/v1.73/README.md) for hashes, checksums, and validation limits. Using the supplied license file with its corresponding version follows the original packaging; it is not a tested guarantee of acceptance on your controller.

## Prepare the USB drive

1. Use an empty USB flash drive. Back up anything on it before clearing it.
2. Copy the chosen patched `.uc3` file to the drive's root and rename that copy to **`DTX9003.uc3`**. Leave the original file in the repository as it is.
3. Then copy the matching **`license.key`** to the drive's root. Copy it as a file; do not open and re-save it in a text editor. These supplied files contain nonprinting bytes.
4. Check that the drive contains the two files below, rather than a ZIP archive, a containing folder, or a file ending in `.uc3.uc3`. Eject the drive cleanly.

```text
USB drive/
├── DTX9003.uc3
└── license.key
```

The manual specifies copying the firmware first and the license file second. It does not specify a filesystem format or USB capacity, so I have not assumed a particular one here.

## Run the update

1. With safe access to the controller's USB port arranged, insert the prepared drive.
2. In the 2014 manual's interface, open **Menu → Fitters settings → Next**, then select **Download** beside **New software**. Confirm the download prompt. Other controller layouts may use different labels; the series manual lists **New software** in its technical settings menu.
3. Let the update finish without removing the drive or interrupting power. The 2014 manual describes a black screen for roughly **15–20 seconds**, followed by the EKOPOWER logo and a countdown from five. That is the manual's expected sequence, not a measured time for these patches.
4. After that sequence completes, remove the USB drive and have any opened housing safely reassembled before normal use.

If the controller rejects the files or does not return to its normal interface, do not assume the update succeeded or repeatedly power-cycle it. Record what happened and consult the controller's service support; this project has no verified bootloader recovery procedure.

## Check before restarting the boiler

Open **Info** and check the software label: **v1.72.42** or **v1.73.42**, depending on the image you chose. The original build date should still appear alongside it. The physical layout of the longer label has not been checked on the display.

Verify the boiler model is **EkoHeat 1500**, then compare all settings with your record and restore the pellet calibration if it was reset. The 2014 manual describes selecting the boiler size under **Menu → Self test**; use the model-selection instructions that match your controller, and avoid activating unrelated test outputs.

Only resume normal operation after the model, calibration, settings, and any faults have been checked. The label alone does not prove that the motor timing or other physical behavior works correctly.
