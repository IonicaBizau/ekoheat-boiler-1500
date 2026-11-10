# Original 1.72 with the automatic clock disabled

The [USB-ready pair](../../../update-v1.72-no-clock/) contains only DTX9003.uc3 and the original 1.72 license.key. All version, date, motor, and startup bytes match original 1.72. Info therefore still reports 1.72.

| Field | Value |
| --- | --- |
| Source firmware SHA-256 | b5ab1b7380f2486c29cf6708954cdb5bbaa2d7798fd0103f845fa254da51a5e8 |
| Derivative firmware SHA-256 | 25bd8691cfc0150dd1f20fb035154a5dcaa8fc666d08cb76633173584137fd02 |
| License SHA-256 | fafba0527c3953c4b6e0e5b5739ba83612f8053bcdc9466730193cd1d590b408 |
| Image size | 450509 bytes |
| Idle instruction | 0x8000B964, file offset 0x397D: 30 08 → 36 48 |
| Payload CRC32 | 42452353 → DB18B81D |

The instruction changes MOV R8,0 to MOV R8,100 in the idle-expiry path. It targets the automatic inactivity transition, not explicit clock selection. The verifier allows only the two instruction bytes and four CRC bytes to differ from the original.

    python3 analysis/tools/patch_v172_no_clock.py
    python3 analysis/tools/verify_v172_no_clock.py

The reported controller attempt left the clock appearing, so the intended behavior was not observed. The [story](../../../docs/firmware-story.md) keeps this result separate from offline verification.
