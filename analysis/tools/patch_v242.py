#!/usr/bin/env python3
"""Build v2.42 from stock v1.73 and prepare a two-file USB update folder."""
import json
from pathlib import Path

import patch_firmware as patch
from verify_v242 import verify


def main():
    patch.SOURCE = Path('DTX9003 v1.73/DTX9003.uc3')
    patch.OUTPUT = Path('analysis/patched/v2.42/DTX9003.uc3')
    patch.EXPECTED_SHA256 = 'e57bb9517c66e8f37ecb864daca5735bc14e3ef6a2614c94a962dc62809f2e3a'
    patch.FIRMWARE_VERSION = '2.42'
    patch.PATCHES = [
        (0x80015130, b'v%d.%02d  %s\0\0\0\0Jul 13 2016\0'.hex(),
         b'v2.42  Nov  8 2026\0'.ljust(28, b'\0').hex(),
         'Info label: v2.42 with custom date 2026-11-08, in the existing 28-byte allocation'),
        (0x8000ba8e, '3008', '3648',
         'Idle expiry: MOV R8,0 -> MOV R8,100; prevent the automatic idle-clock path'),
    ]
    update_dir = Path('update-v2.42')
    names = {'DTX9003.uc3', 'license.key'}
    if update_dir.exists() and (not update_dir.is_dir() or update_dir.is_symlink()):
        raise SystemExit('Update destination must be a regular directory')
    if update_dir.exists():
        entries = list(update_dir.iterdir())
        if any(p.name not in names or not p.is_file() or p.is_symlink() for p in entries):
            raise SystemExit('Update directory contains unexpected entries; no files changed')

    patch.main()
    verify()  # Independent, fixed expectations; do not package an unverified image.
    update_dir.mkdir(exist_ok=True)
    for name in sorted(names):
        (update_dir / name).write_bytes((patch.OUTPUT.parent / name).read_bytes())
    result = verify(update_dir)
    report = json.dumps(result, indent=2) + '\n'
    (patch.OUTPUT.parent / 'verification.json').write_text(report)
    print(report, end='')


if __name__ == '__main__':
    main()
