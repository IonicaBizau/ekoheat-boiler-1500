# v2.73 update investigation

The user reported that the update did not load, with similar behavior previously seen on another USB drive. This time it occurred with a drive that had worked before. No specific rejection message or currently running version was provided. No firmware change is justified as an update fix from this report alone.

## Rechecked files

- v2.73 is 453229 bytes, the same length as the supplied v1.73 image.
- The 21-byte wrapper prefix is unchanged. Its `AVR32` signature is intact.
- Stored big-endian payload CRC32 is `3DA58A4D` for the five-attempt rebuild, matching the CRC32 of bytes from offset 25 through EOF.
- The supplied license remains byte-for-byte identical to the v1.73 source (`34 1C`). Its validation algorithm is unknown; matching the supplied license does not prove acceptance of modified firmware.
- Exactly 16 bytes differ from the source: four CRC bytes, two idle-expiry bytes, seven opening-allowance bytes, one displayed-major-version byte, and two startup-counter bytes. These are the changes recorded in the manifest.
- The displayed major argument is 2; minor argument 73, format, and build date remain intact. This check does not establish whether the updater has any additional version policy.
- Original source hashes, generated output hash, instruction checks, and 326777 opening-time comparisons pass.

The supplied application payload starts at `0x80008000`; it does not include the lower flash region. No updater acceptance algorithm has been established from this application analysis. Do not infer a signature requirement, license fix, or version rejection from the failure report alone.

`verify_patch.py` now checks the wrapper and supplied license explicitly and accepts `--update-dir` to compare both USB files byte-for-byte against the verified build. It reads the USB files without changing them:

```sh
python3 analysis/tools/verify_patch.py --version 1.73 --update-dir /Volumes/USB_NAME
```

## Startup attempts

The original v1.73 state machine at `0x80024100` uses an 8-bit counter at RAM `0x2365`. It increments after the configured ignition wait and retries while the new count is below 3. Machine instructions at `0x80024440` through `0x80024446` compare that count with 2 and branch to the failure assignment if it is higher. Thus normal startup has three attempts.

There is also a separate fuel-charge gate: the entry code only recalculates charging while the count is below 2 (`0x80024288` through `0x8002428E`). The first charge uses the initial quantity, and the second uses a quarter-based calculation. The third bypasses that charging setup. Increasing the retry comparison alone does not define a new fuel-charge sequence.

The ignition routine at `0x8000ED44` additionally seeds the counter to 3 on the `0x22F3 == 2` path. Raising the limit could change this path as well as normal startup. It also keeps the ignition request active until light detection, so a higher retry limit can extend ignition operation. The separate startup-ramp low-light failure remains a different cause of “Startup failed!” and would not be fixed by extra attempts.

The user requested five total attempts. The rebuild changes the limit comparison to 4 and the special-path exhausted seed to 5, retaining that path's first-timeout failure. Charging conditions are unchanged. Independent native decompilation confirms both edits; the verifier checks five failed waits and unchanged remaining routine bytes. Physical ignition duty limits remain unverified. The earlier three-attempt v2.73 had CRC32 `DD3E71AC`; the rebuilt image has CRC32 `3DA58A4D`. This startup change is not claimed to fix USB loading. Evidence: [state machine](v1.73/decompiled/80024100.txt), [ignition routine](v1.73/decompiled/8000ed44.txt), and [original startup-failure analysis](startup-failure.md).
