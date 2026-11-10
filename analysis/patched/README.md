# Patched firmware

Each patch has its own folder. The firmware keeps the original **`DTX9003.uc3`** filename, with its matching **`license.key`** beside it. The folder identifies the version and changes.

| Folder | Changes |
| --- | --- |
| [v2.42](v2.42/README.md) | Minimal patch from original v1.73: no automatic idle clock; Info label `v2.42  Nov  8 2026`. Two-file USB package: [update-v2.42](../../update-v2.42/). |
| [v1.72.42](v1.72.42/README.md) | Screen stays awake; 30 extra seconds for ash-plate opening; custom version label. |
| [v2.73](v2.73/README.md) | Screen stays awake; 30 extra opening seconds; five total normal startup attempts; custom version label. Based on original v1.73. |

Each folder also contains the patch manifest and supporting evidence. Copy `DTX9003.uc3` first, then `license.key`, to the USB drive's root. See [Updating the boiler software](../../docs/updating-firmware.md) for the full manual-based procedure and settings checks.

These images have been checked offline. A reported v2.42 update attempt did not show its expected label or clock behavior; bootloader acceptance and physical operation remain unverified. See the [update investigation](../update-investigation.md).
