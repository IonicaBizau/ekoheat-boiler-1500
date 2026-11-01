<!-- Generated with blah. Edit the blah field in package.json or .blah/README.ejs, then run npm run readme. -->

[![Ekoheat 1500](media/header.svg)](#fire-why-this-exists)

# Ekoheat 1500

[![Support me on Patreon](https://ionicabizau.github.io/badges/patreon.svg)](https://www.patreon.com/ionicabizau) [![Ask me anything](https://img.shields.io/badge/ask%20me-anything-1abc9c.svg)](https://github.com/IonicaBizau/ama) [![Firmware](https://img.shields.io/badge/firmware-1.72%20%7C%201.73-ef8e46)](analysis/v1.73/comparison.md) [![Validation](https://img.shields.io/badge/validation-static%20only-64748b)](analysis/patched/v1.73/README.md)

> Reverse engineering, firmware notes, and small quality-of-life patches for the Ekoheat 1500 pellet boiler.

## :fire: Why this exists

A pellet boiler should be easier to understand than a mystery box with a touchscreen. This project documents the Ekoheat 1500 controller, compares its DTX9003 firmware, and keeps small, reproducible patches alongside the evidence behind them.

The first quality-of-life fix: **keep the current screen visible instead of switching to the idle clock**.

This is independent research based on static binary analysis. The patches have been checked offline; **controller execution and bootloader acceptance have not been tested**.

## :sparkles: What is inside

- **v1.72 → v1.73 comparison** — low-fuel warnings, richer status messages, pump-control changes, UI assets, and input handling.
- **Minimal v1.73 clock-screen patch** — two instruction bytes and the CRC32 field; keeps the display active when the inactivity timer expires.
- **Earlier v1.72 patch** — keeps the display active and extends the ash-plate opening allowance from 10 to 30 seconds beyond the configured movement time.
- **Firmware evidence** — native disassembly, decompiled routines, hashes, checksums, and manifests.
- **Controller notes and manuals** — ignition behavior, calibration findings, wiring references, and extracted bitmap previews.

## :cloud: Getting started

You need **Python 3.6+** for the patch scripts. They use the standard library; Node.js is only needed to regenerate this README.

```sh
git clone https://github.com/ionicabizau/ekoheat-boiler-1500.git
cd ekoheat-boiler-1500
```

Start with the [firmware comparison](analysis/v1.73/comparison.md), [changelog](CHANGELOG.md), or [interesting findings](FUN_FACTS.md).

## :wrench: Keep the screen awake on v1.73

Run from the repository root:

```sh
python3 analysis/tools/patch_v173_no_idle_clock.py
```

The script checks the source SHA-256 and CRC32, creates the derivative, verifies the changed regions and checksum, and confirms the source is unchanged.

| File | Purpose |
| --- | --- |
| [`DTX9003 v1.73/DTX9003.uc3`](DTX9003%20v1.73/DTX9003.uc3) | Original v1.73 source image |
| [`DTX9003_no_idle_clock.uc3`](analysis/patched/v1.73/DTX9003_no_idle_clock.uc3) | Patched image |
| [JSON manifest](analysis/patched/v1.73/DTX9003_no_idle_clock.json) | SHA-256 values, CRC32, offsets, and verification results |
| [Patch notes](analysis/patched/v1.73/README.md) | Instruction changes and supporting evidence |

The instruction at `0x8000BA8E` changes from `MOV R8,0` to `MOV R8,100`. At inactivity expiry, the firmware keeps the active brightness request rather than triggering the fade that leads to the clock screen. The timer still expires for other UI uses.

**This v1.73 patch changes display behavior only.**

## :hourglass_flowing_sand: Earlier v1.72 patch

```sh
python3 analysis/tools/patch_firmware.py
python3 analysis/tools/verify_patch.py
```

This produces [`DTX9003_no_idle_clock_30s.uc3`](analysis/patched/DTX9003_no_idle_clock_30s.uc3). Alongside the display change, it increases the ash-plate opening allowance to 30 seconds beyond the configured movement duration. This changes motor fault timing; read the [full patch notes](analysis/patched/README.md) before considering it.

Offsets and patch instructions are specific to each source image. Both generators refuse a source with a different SHA-256.

## :mag: What the binaries tell us

| Finding | Evidence |
| --- | --- |
| Ignition detection uses a processed light threshold of 18 lux; three failed attempts can produce “Startup failed!” | [Startup analysis](analysis/startup-failure.md) |
| Three ash-plate endstop activations within five seconds appear to request touchscreen recalibration on next startup | [Calibration notes](FUN_FACTS.md) |
| v1.73 adds low-fuel warning and expanded communication/status fields | [Version comparison](analysis/v1.73/comparison.md) |
| v1.73 adds start/standby/shutdown reactions to a digital input | [Input analysis](analysis/v1.73/comparison.md#additional-response-to-digital-input-gpio-0x20) |
| One manual documents an ambient thermostat connection on J1 terminals 8–9 | [Manual index](docs/README.md) |

The mapping between that thermostat connection and firmware GPIO `0x20` is **unconfirmed**. Remote error acknowledgement is also unverified. A physical safety cut-out may require a physical reset; clearing a UI message does not repair its cause.

## :file_folder: Repository map

| Path | Contents |
| --- | --- |
| [`Ecoheat_v1.72/`](Ecoheat_v1.72/) | Original v1.72 firmware |
| [`DTX9003 v1.73/`](DTX9003%20v1.73/) | Original v1.73 firmware |
| [`analysis/tools/`](analysis/tools/) | Python patch/analysis scripts and SLEIGH disassembler source |
| [`analysis/patched/`](analysis/patched/) | Derivatives, manifests, and patch evidence |
| [`analysis/v1.73/`](analysis/v1.73/) | Version comparison and decompiled v1.73 routines |
| [`analysis/ghidra/`](analysis/ghidra/) | Original v1.72 disassembly and decompiled routines |
| [`analysis/assets/`](analysis/assets/) | Extracted RGB565 bitmap previews and HTML viewer |
| [`docs/`](docs/) | Boiler manuals and display datasheet |

See [analysis setup and reproduction](analysis/README.md) for the distinction between Python-only tools and the native Ghidra tooling. Local native builds, generated XML images, caches, and `license.key` files are excluded from Git.

## :memo: Regenerate this README

The content lives in the **`blah` field of [`package.json`](package.json)**. The project-local template is [`.blah/README.ejs`](.blah/README.ejs).

```sh
npm ci
npm run readme
```

Or, with [`blah`](https://github.com/ionicabizau/blah) already installed:

```sh
blah --readme
```

The checked-in template follows my GitHub README conventions and renders without depending on `~/.blah-templates` or fetching npm dependents. Edit the metadata or template, then regenerate `README.md`.

## :yum: How to contribute

Found another firmware version, identified an input, or spotted an incorrect interpretation? [Open an issue](https://github.com/ionicabizau/ekoheat-boiler-1500/issues) or send a pull request. Include the firmware hash and the evidence supporting the finding.

See [CONTRIBUTING.md](CONTRIBUTING.md) for patch-validation and documentation guidelines.

## :sparkling_heart: Support my projects

If this project helps, give it a star or share what you discover. :heart:

[Support me on Patreon](https://www.patreon.com/ionicabizau) · [Buy me a coffee](https://www.buymeacoffee.com/H96WwChMy) · [PayPal](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=RVXDDLKKLQRJW)

## :scroll: License

Original project scripts, documentation, and header artwork: [MIT](LICENSE) © [Ionică Bizău](https://ionicabizau.net).

Vendor firmware, patched derivatives, extracted assets, and supplied manuals retain their respective owners’ rights and are excluded from that license grant. See [THIRD_PARTY.md](THIRD_PARTY.md). This project is not affiliated with or endorsed by Ekopower.
