# Ekoheat 1500 firmware notes

This repository keeps two original DTX9003 firmware releases and one minimal clock-only derivative of each. The update folders contain only the two files to copy to a USB drive.

| Firmware | Folder | Info version | Intended idle behavior |
| --- | --- | --- | --- |
| Original 1.72 | [DTX9003 v1.72](DTX9003%20v1.72/) | 1.72 | Clock appears |
| 1.72, no clock | [update-v1.72-no-clock](update-v1.72-no-clock/) | 1.72 | Automatic clock disabled |
| Original 1.73 | [DTX9003 v1.73](DTX9003%20v1.73/) | 1.73 | Clock appears |
| 1.73, no clock | [update-v1.73-no-clock](update-v1.73-no-clock/) | 1.73 | Automatic clock disabled |

The two derivatives each change one AVR32 idle-expiry instruction and the required payload CRC32. Their original version and date bytes, control logic, and matching vendor license files are preserved. A matching Info version alone cannot prove that either derivative installed.

The [story and controller observations](docs/firmware-story.md) explain the earlier v2.42 experiments, including the latest report: after official 1.73 installed, two v2.42 attempts left Info at 1.73 while the clock appeared to stay away. The exact installed image and persistence have not been verified. The v2.42 and older motor/startup derivatives have been removed from the current file set; they remain in Git history.

For USB preparation and checks, use the [update guide](docs/updating-firmware.md). For the binary comparison, see [analysis](analysis/README.md). The underlying firmware belongs to its original owner; see [third-party materials](THIRD_PARTY.md).
