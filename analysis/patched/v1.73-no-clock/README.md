# Original 1.73 with the automatic clock disabled

The [USB-ready pair](../../../update-v1.73-no-clock/) contains only DTX9003.uc3 and the original 1.73 license.key. All version, date, motor, and startup bytes match original 1.73. Info therefore still reports 1.73.

| Field | Value |
| --- | --- |
| Source firmware SHA-256 | e57bb9517c66e8f37ecb864daca5735bc14e3ef6a2614c94a962dc62809f2e3a |
| Derivative firmware SHA-256 | dec5a6496a4688258a0566d9b33cdf61f9497d18912310e097b71bf91972503e |
| License SHA-256 | 8075e4bc145fadd645f7edfe2ec00c0b644b5a6edef3349531d5ff4cc155c3b5 |
| Image size | 453229 bytes |
| Idle instruction | 0x8000BA8E, file offset 0x3AA7: 30 08 → 36 48 |
| Payload CRC32 | A69EA7CF → C097A83F |

The instruction changes MOV R8,0 to MOV R8,100 in the idle-expiry path. It targets the automatic inactivity transition, not explicit clock selection. The verifier allows only the two instruction bytes and four CRC bytes to differ from the original.

    python3 analysis/tools/patch_v173_no_clock.py
    python3 analysis/tools/verify_v173_no_clock.py

An earlier attempt to load this clock-only pair reportedly failed. A later v2.42 attempt seemed to disable the clock but left Info at 1.73; that observation does not identify the image installed. See the [story](../../../docs/firmware-story.md).
