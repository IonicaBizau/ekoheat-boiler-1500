#!/usr/bin/env python3
"""Build a stock-v1.73 derivative changing only automatic idle expiry."""
import hashlib
import struct
import zlib
from pathlib import Path

SOURCE = Path('DTX9003 v1.73/DTX9003.uc3')
OUTPUT_DIR = Path('update-v1.73-no-clock')
SOURCE_SHA256 = 'e57bb9517c66e8f37ecb864daca5735bc14e3ef6a2614c94a962dc62809f2e3a'
LICENSE_SHA256 = '8075e4bc145fadd645f7edfe2ec00c0b644b5a6edef3349531d5ff4cc155c3b5'
IDLE_OFFSET = 0x3aa7


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    original = SOURCE.read_bytes()
    license_bytes = SOURCE.with_name('license.key').read_bytes()
    if sha(original) != SOURCE_SHA256 or sha(license_bytes) != LICENSE_SHA256:
        raise SystemExit('Original firmware or license differs from the verified v1.73 pair')
    if struct.unpack_from('>I', original, 21)[0] != zlib.crc32(original[25:]):
        raise SystemExit('Original payload CRC32 is invalid')
    if original[IDLE_OFFSET:IDLE_OFFSET + 2] != bytes.fromhex('3008'):
        raise SystemExit('Original idle instruction differs')
    if OUTPUT_DIR.exists():
        if not OUTPUT_DIR.is_dir() or OUTPUT_DIR.is_symlink():
            raise SystemExit('Output path is not a regular directory')
        entries = list(OUTPUT_DIR.iterdir())
        if {entry.name for entry in entries} - {'DTX9003.uc3', 'license.key'}:
            raise SystemExit('Output directory contains unexpected entries')
        if any(not entry.is_file() or entry.is_symlink() for entry in entries):
            raise SystemExit('Output directory contains an invalid file')

    patched = bytearray(original)
    patched[IDLE_OFFSET:IDLE_OFFSET + 2] = bytes.fromhex('3648')
    struct.pack_into('>I', patched, 21, zlib.crc32(patched[25:]))
    OUTPUT_DIR.mkdir(exist_ok=True)
    (OUTPUT_DIR / 'DTX9003.uc3').write_bytes(patched)
    (OUTPUT_DIR / 'license.key').write_bytes(license_bytes)
    print('Firmware SHA-256:', sha(patched))
    print('License SHA-256:', sha(license_bytes))


if __name__ == '__main__':
    main()
