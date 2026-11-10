# Contributing

Please include the exact firmware SHA-256, virtual address and file offset for a binary finding, along with the disassembly or other evidence. Separate static predictions from controller observations.

The original images must remain unchanged. For the two retained derivatives, run:

    python3 analysis/tools/patch_v172_no_clock.py
    python3 analysis/tools/verify_v172_no_clock.py
    python3 analysis/tools/patch_v173_no_clock.py
    python3 analysis/tools/verify_v173_no_clock.py

Do not treat a passing offline verifier as evidence that the controller accepted an image. Keep unrelated credentials, native builds, and caches out of commits. Third-party firmware and manuals retain their original ownership; see [THIRD_PARTY.md](THIRD_PARTY.md).
