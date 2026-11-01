# :yum: How to contribute

If you have another firmware version, a correction, or a better way to do something here, I would love to hear about it. Issues and pull requests are welcome.

## Firmware findings

Include the source image's SHA-256, firmware version, addresses/file offsets, and supporting disassembly or decompilation. Please say what you found in the code, what you think it means, and what you have tested on hardware. Do not describe the unidentified GPIO as a confirmed thermostat input.

## Patches

Keep original images intact. Guard against the wrong source hash, verify the payload CRC32, record every allowed byte change, and preserve image size unless a format change is deliberate and documented. Report what was statically checked and whether hardware execution occurred. Do not treat passing checksum checks as proof of safe operation or update acceptance.

For the existing patches, run from the repository root:

```sh
python3 analysis/tools/patch_v173_no_idle_clock.py
python3 analysis/tools/patch_firmware.py
python3 analysis/tools/verify_patch.py
```

## README edits

Edit `package.json` under `blah`, or `.blah/README.ejs` for layout changes, then run:

```sh
npm ci
npm run readme
```

Commit the generated `README.md` with its source changes. Python-only patching does not require npm.

The supplied firmware `license.key` files are included. Keep unrelated credentials, native builds, and caches out of commits. Respect the third-party materials described in [THIRD_PARTY.md](THIRD_PARTY.md).
