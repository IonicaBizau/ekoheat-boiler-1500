# Firmware analysis

The current files are the two [original releases](../README.md) and their two minimal clock-only derivatives. The [firmware story](../docs/firmware-story.md) records the retired experiments and hardware observations.

From the repository root, rebuild and verify the current derivatives:

    python3 analysis/tools/patch_v172_no_clock.py
    python3 analysis/tools/verify_v172_no_clock.py
    python3 analysis/tools/patch_v173_no_clock.py
    python3 analysis/tools/verify_v173_no_clock.py

The generators require exact source hashes, replace one two-byte idle instruction without moving data, recalculate the payload CRC32, and copy the original matching license. Each independent verifier reconstructs the expected image and checks the two-file package. Neither generator flashes the controller.

Original images use a 25-byte wrapper. The payload begins at virtual address 0x80008000, so a file offset maps to a virtual address by adding 0x80007FE7. The big-endian payload CRC32 at file offset 0x15 covers bytes from offset 0x19 through EOF. The application images do not include the controller's lower flash region or updater.

The original [1.72/1.73 comparison](v1.73/comparison.md), [startup analysis](startup-failure.md), and [asset extraction notes](assets/README.md) remain as research references. Native disassembly requires Ghidra AVR32-A big-endian SLEIGH support. Decompiled variable names and function matching are analysis aids, not verified vendor source.
