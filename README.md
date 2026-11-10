![Illustrated Ekoheat 1500 boiler and awake display](media/header.svg)

# 🔥 Ekoheat 1500

![Firmware 1.72 and 1.73](https://img.shields.io/badge/firmware-1.72%20%7C%201.73-f3a34a)
![Four active variants](https://img.shields.io/badge/active%20variants-4-57b894)
![Static verification](https://img.shields.io/badge/verification-static%20bytes-6b8eaa)

Firmware research, controller notes, and a small display change for the Ekoheat 1500 pellet boiler. The goal is simple: **keep the normal screen visible instead of switching to the idle clock**.

## 🧭 Start here

| I want to… | Read |
| --- | --- |
| Understand startup, buttons, menus, and alarms | [Alternative controller guide](docs/controller-guide.md) |
| Prepare a USB update and check settings afterward | [Firmware update guide](docs/updating-firmware.md) |
| Follow what happened during the update attempts | [Firmware story](docs/firmware-story.md) |
| Explore the binary findings | [Analysis index](analysis/README.md) · [1.72/1.73 comparison](analysis/v1.73/comparison.md) |

## 🧩 Four firmware variants

Each folder contains an image named **DTX9003.uc3** and its matching **license.key**. Choose one pair at a time for a USB update.

| Source release | Original 📦 | Clock-only derivative 🌿 | Info text if installed |
| --- | --- | --- | --- |
| **1.72** | [Original 1.72](DTX9003%20v1.72/) | [1.72, no clock](update-v1.72-no-clock/) | 1.72 |
| **1.73** | [Original 1.73](DTX9003%20v1.73/) | [1.73, no clock](update-v1.73-no-clock/) | 1.73 |

The clock-only images change one idle-expiry instruction and the required payload CRC32. Their version, date, motor, startup, and license bytes stay matched to their original release. See the [1.72 patch notes](analysis/patched/v1.72-no-clock/README.md) and [1.73 patch notes](analysis/patched/v1.73-no-clock/README.md) for exact hashes and offsets.

> [!IMPORTANT]
> A matching Info version does not identify which of the two images for that release is installed. The files pass offline byte checks, but the controller's acceptance rule and installed flash contents have not been established.

## 🕰️ What the controller showed

An earlier v2.42 experiment tried to change the Info label as well as the clock behavior. After official 1.73 was installed, two v2.42 attempts left Info showing **1.73**, while the clock later **seemed to stay away**. The exact installed image and persistence after a normal restart remain unconfirmed. The v2.42 package and older motor/startup experiments are kept in Git history, outside the four active variants. The [full story](docs/firmware-story.md) records each observation.

## 🔬 Rebuild and verify

From the repository root, Python 3 runs the current build and verification tools:

    python3 analysis/tools/patch_v172_no_clock.py
    python3 analysis/tools/verify_v172_no_clock.py
    python3 analysis/tools/patch_v173_no_clock.py
    python3 analysis/tools/verify_v173_no_clock.py

These commands create local files and check their bytes; they do not update the boiler. The [analysis notes](analysis/README.md) explain the firmware wrapper and address mapping.

## 📚 More

[Manuals and references](docs/README.md) · [Startup-failure analysis](analysis/startup-failure.md) · [Changelog](CHANGELOG.md) · [Contributing](CONTRIBUTING.md) · [Third-party materials](THIRD_PARTY.md)
