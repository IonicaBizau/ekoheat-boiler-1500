<!-- Generated with blah. Edit the blah field in package.json or .blah/README.ejs, then run npm run readme. -->

[![Ekoheat 1500](media/header.svg)](#fire-why-this-exists)

# Ekoheat 1500

[![Support me on Patreon](https://ionicabizau.github.io/badges/patreon.svg)](https://www.patreon.com/ionicabizau) [![Ask me anything](https://img.shields.io/badge/ask%20me-anything-1abc9c.svg)](https://github.com/IonicaBizau/ama) [![Firmware](https://img.shields.io/badge/firmware-1.72%20%7C%201.73-ef8e46)](analysis/v1.73/comparison.md) [![Validation](https://img.shields.io/badge/validation-static%20only-64748b)](analysis/patched/v1.73/README.md)

> Reverse engineering, firmware notes, and small quality-of-life patches for the Ekoheat 1500 pellet boiler.

## :fire: Why this exists

I own an **EkoHeat 1500 pellet boiler**, and I wanted to personalize it more for my needs. So I started looking into its DTX9003 firmware, figuring out how it works, and making a few small changes.

The first thing I wanted: **keep the current screen visible instead of switching to the idle clock**. :)

This repo is where I keep my notes, tools, firmware comparisons, and patches. I have checked the patches offline, but **I have not tested them on the controller or checked whether the bootloader accepts them**.

## :sparkles: What is inside

Here is what I have put together so far:

- A **v1.72 → v1.73 comparison**, covering low-fuel warnings, status messages, pump control, and UI changes.
- A **v1.73 patch to keep the screen awake**. It changes two instruction bytes and updates the checksum.
- An **earlier v1.72 patch** that also gives the ash plate more time to open: 30 seconds beyond the configured movement time, up from 10.
- Disassembly, decompiled routines, hashes, and checksums so you can follow the findings.
- Manuals and notes about ignition, touchscreen calibration, wiring, and the images used by the display.

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

The script checks the source SHA-256 and CRC32, writes the patched file, verifies the changed regions and checksum, and confirms the source is unchanged.

| File | Purpose |
| --- | --- |
| [`DTX9003 v1.73/DTX9003.uc3`](DTX9003%20v1.73/DTX9003.uc3) | Original v1.73 source image |
| [`DTX9003_no_idle_clock.uc3`](analysis/patched/v1.73/DTX9003_no_idle_clock.uc3) | Patched image |
| [JSON manifest](analysis/patched/v1.73/DTX9003_no_idle_clock.json) | SHA-256 values, CRC32, offsets, and verification results |
| [Patch notes](analysis/patched/v1.73/README.md) | Instruction changes and supporting evidence |

The instruction at `0x8000BA8E` changes from `MOV R8,0` to `MOV R8,100`. When the inactivity timer expires, the firmware keeps the display bright, which prevents the automatic switch to the clock screen. The timer still expires for other UI uses.

**This v1.73 patch changes display behavior only.**

## :hourglass_flowing_sand: Earlier v1.72 patch

```sh
python3 analysis/tools/patch_firmware.py
python3 analysis/tools/verify_patch.py
```

This produces [`DTX9003_no_idle_clock_30s.uc3`](analysis/patched/DTX9003_no_idle_clock_30s.uc3). I also increased the ash-plate opening allowance to 30 seconds beyond the configured movement duration. This changes motor fault timing; read the [full patch notes](analysis/patched/README.md) for the details.

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
| [`DTX9003 v1.72/`](DTX9003%20v1.72/) | Original v1.72 firmware |
| [`DTX9003 v1.73/`](DTX9003%20v1.73/) | Original v1.73 firmware |
| [`analysis/tools/`](analysis/tools/) | Python patch/analysis scripts and SLEIGH disassembler source |
| [`analysis/patched/`](analysis/patched/) | Derivatives, manifests, and patch evidence |
| [`analysis/v1.73/`](analysis/v1.73/) | Version comparison and decompiled v1.73 routines |
| [`analysis/ghidra/`](analysis/ghidra/) | Original v1.72 disassembly and decompiled routines |
| [`analysis/assets/`](analysis/assets/) | Extracted RGB565 bitmap previews and HTML viewer |
| [`docs/`](docs/) | Boiler manuals and display datasheet |

See [analysis setup and reproduction](analysis/README.md) for the distinction between Python-only tools and the native Ghidra tooling. The supplied `license.key` files are included in their firmware folders. They are not needed for offline analysis or patch generation. Local native builds, generated XML images, and caches are excluded from Git.

## :memo: Regenerate this README

I use [`blah`](https://github.com/ionicabizau/blah) for this README. Edit the **`blah` field in [`package.json`](package.json)**, or [`.blah/README.ejs`](.blah/README.ejs) for layout changes, then run:

```sh
npm ci
npm run readme
```

Commit the generated README along with the source changes.

## :yum: How to contribute

Found another firmware version, figured out an input, or noticed something I got wrong? [Open an issue](https://github.com/ionicabizau/ekoheat-boiler-1500/issues) or send a pull request. Please include the firmware hash and how you reached your conclusion.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the details.

## :sparkling_heart: Support my projects

If this project helps, give it a star or share what you discover. :heart:

[Support me on Patreon](https://www.patreon.com/ionicabizau) · [Buy me a coffee](https://www.buymeacoffee.com/H96WwChMy) · [PayPal](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=RVXDDLKKLQRJW)

## :scroll: License

Original project scripts, documentation, and header artwork: [MIT](LICENSE) © [Ionică Bizău](https://ionicabizau.net).

Vendor firmware, patched derivatives, extracted assets, and supplied manuals retain their respective owners’ rights and are excluded from that license grant. See [THIRD_PARTY.md](THIRD_PARTY.md). This project is not affiliated with or endorsed by Ekopower.
