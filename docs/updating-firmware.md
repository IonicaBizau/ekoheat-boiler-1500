# Updating the boiler software

For the boiler's initial setup and its normal startup sequence, see the [alternative controller guide](controller-guide.md). This page covers USB firmware loading.

The [2014 Ekoheat manual, page 16](ekopower%20ekoheat%20installation%20manual%202%202014%20eng.pdf#page=16) says to use an empty USB drive and copy DTX9003.uc3 first, then its matching license.key. Follow the menu labels on the controller fitted to the boiler. Finish its normal shutdown before an update and keep power stable during the update.

Choose **one** pair and put its two files at the USB root:

| Version | Firmware and matching license |
| --- | --- |
| Original 1.72 | [DTX9003 v1.72](../DTX9003%20v1.72/) |
| 1.72, no automatic clock | [update-v1.72-no-clock](../update-v1.72-no-clock/) |
| Original 1.73 | [DTX9003 v1.73](../DTX9003%20v1.73/) |
| 1.73, no automatic clock | [update-v1.73-no-clock](../update-v1.73-no-clock/) |

Copy the files themselves, not their containing folder. On macOS, use a cleanly ejected drive and inspect the root for AppleDouble files whose names begin with **._**. Such files were found on one attempted update drive; whether they affect this controller is unknown. A fresh or cleared spare drive is a useful comparison. The manual does not specify a filesystem format or partition scheme.

## On the controller

1. Record Info version, selected model, pellet calibration, and other settings. Stop the boiler through its normal Stop button and let shutdown finish.
2. Insert the prepared USB drive. On the 2014 layout, open **Menu → Fitters settings → Next**, then press **Download** beside **New software** and confirm. The later series manual places **New software** under **Service**. The manuals reserve this action for authorised personnel.
3. Leave the drive and power in place during loading. The 2014 manual describes a black screen for roughly 15–20 seconds, followed by the EKOPOWER logo and a countdown from five. Remove the USB when the documented sequence finishes.
4. Check the selected model and restore calibration and settings if they changed. Open Info and record the version, then check the idle screen after more than four minutes and again after a normal restart. A countdown or touchscreen recalibration prompt alone does not identify the firmware that ran.

To compare a copied clock-only pair with its verified build, run from the repository root:

    python3 analysis/tools/verify_v172_no_clock.py --update-dir "/Volumes/YOUR_USB_NAME"
    python3 analysis/tools/verify_v173_no_clock.py --update-dir "/Volumes/YOUR_USB_NAME"

Run only the command for the chosen pair. The check verifies USB file contents; it cannot prove controller acceptance. The clock-only builds retain their original Info labels, so check the screen after more than four minutes without touching it and after a normal restart. See the [story](firmware-story.md) for the reported outcomes.

The manual warns that an update may reset all settings and select Ekoheat 900. Record the current boiler model, pellet calibration, and settings beforehand. Afterward, confirm Ekoheat 1500 is selected and restore any changed settings before normal operation. A touchscreen recalibration prompt is not documented as a required sign of successful application installation.
