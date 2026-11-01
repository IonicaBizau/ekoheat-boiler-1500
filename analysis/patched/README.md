# Patched firmware

Each patch has its own folder. The firmware keeps the original **`DTX9003.uc3`** filename, with its matching **`license.key`** beside it. The folder identifies the version and changes.

| Folder | Changes |
| --- | --- |
| [v1.72.42](v1.72.42/README.md) | Screen stays awake; 30 extra seconds for ash-plate opening; custom version label. |
| [v2.73](v2.73/README.md) | Same changes, based on original v1.73. |

Each folder also contains the patch manifest and supporting evidence. Copy `DTX9003.uc3` first, then `license.key`, to the USB drive's root. See [Updating the boiler software](../../docs/updating-firmware.md) for the full manual-based procedure and settings checks.

These images have been checked offline; flashing, bootloader acceptance, and physical operation remain untested.
