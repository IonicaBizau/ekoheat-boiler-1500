# The firmware update story

This is a record of what was built and what the controller actually showed. A USB update screen, a touchscreen recalibration prompt, and a matching file hash do not by themselves prove which application is running.

For the normal initial setup, startup stages, buttons, and menu entries, see the [alternative controller guide](controller-guide.md).

## What we wanted

The original Ekoheat 1500 controller runs DTX9003 firmware. The requested change was to keep the normal display visible instead of switching to the idle clock. An earlier experiment also tried to show a custom v2.42 label dated 8 November 2026. The original releases available here are 1.72 and 1.73.

## What happened

1. An early modified 1.73 build reportedly kept the clock away while Info still showed 1.73. The exact image installed at that time was not identified. This established an observed screen behavior, not a proven version-label change.
2. A later v2.42 derivative of original 1.73 changed the idle instruction and placed a literal v2.42 label in the application image. An initial controller attempt showed an update sequence and touchscreen recalibration, but Info still showed 1.73 and the clock returned after about four minutes. The USB firmware and license matched the intended package byte for byte.
3. Original 1.72 installed. A v2.42 attempt from 1.72 left Info at 1.72. This ruled out already being on 1.73 as a sufficient explanation for that failure.
4. A clock-only 1.73 derivative was tried and reportedly did not load. A clock-only 1.72 derivative produced no reported error or recalibration prompt, but the clock still appeared. Neither result established which bytes were in flash.
5. An attempt to restore untouched original 1.73 initially failed. A read-only check found the exact original 1.73 firmware and license on the mounted USB drive, together with macOS AppleDouble sidecars and system directories. Those extra entries might matter to a simple updater, but no rule has been demonstrated.
6. On 10 November 2026, the user reported that official 1.73 subsequently installed. Two more v2.42 update attempts left the Info label unchanged at 1.73, but the clock now **seems to be disabled**. The duration of that observation and behavior after a normal restart were not reported. Because the label and clock observations disagree, the exact installed image is still unknown.

The last observation is consistent with the intended clock change taking effect, but it does not prove that the v2.42 image as a whole installed. A previously attempted clock-only image, a different UI version path, or another controller state could also explain the mismatch. The available files include the application payload, not the controller's updater or a read-back of its flash. No license algorithm, rollback mechanism, or acceptance rule has been established.

## Current file set

Only four firmware variants remain in the working tree:

| Variant | Firmware SHA-256 | License SHA-256 |
| --- | --- | --- |
| [Original 1.72](../DTX9003%20v1.72/) | b5ab1b7380f2486c29cf6708954cdb5bbaa2d7798fd0103f845fa254da51a5e8 | fafba0527c3953c4b6e0e5b5739ba83612f8053bcdc9466730193cd1d590b408 |
| [1.72, no clock](../update-v1.72-no-clock/) | 25bd8691cfc0150dd1f20fb035154a5dcaa8fc666d08cb76633173584137fd02 | fafba0527c3953c4b6e0e5b5739ba83612f8053bcdc9466730193cd1d590b408 |
| [Original 1.73](../DTX9003%20v1.73/) | e57bb9517c66e8f37ecb864daca5735bc14e3ef6a2614c94a962dc62809f2e3a | 8075e4bc145fadd645f7edfe2ec00c0b644b5a6edef3349531d5ff4cc155c3b5 |
| [1.73, no clock](../update-v1.73-no-clock/) | dec5a6496a4688258a0566d9b33cdf61f9497d18912310e097b71bf91972503e | 8075e4bc145fadd645f7edfe2ec00c0b644b5a6edef3349531d5ff4cc155c3b5 |

The former v2.42 package had firmware SHA-256 816adffec4f7427acdbc96a06916aac5d324ebbd8e08030205d21b79f4383185. It and the older combined motor/startup patches were removed to keep the active set clear. Git commit 66346a7 contains their previous files and analysis if a historical comparison is needed.

## Next evidence

With the USB removed, leave the same screen untouched longer than the previously observed four-minute idle interval, then repeat after a normal restart. Record the exact Info text and whether the clock appears on each check. Verify the boiler model is Ekoheat 1500 and compare calibration and settings with the pre-update record. To identify exact installed bytes, a qualified technician would need a read-only flash dump or a documented controller diagnostic; the chip's security bit may prevent a non-destructive dump. Do not clear that bit with a chip erase.
