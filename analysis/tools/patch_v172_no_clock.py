#!/usr/bin/env python3
"""Build a stock-v1.72 derivative changing only automatic idle expiry."""
import hashlib
import struct
import zlib
from pathlib import Path

SOURCE = Path('DTX9003 v1.72/DTX9003.uc3')
OUTPUT_DIR = Path('update-v1.72-no-clock')
SOURCE_SHA256 = 'b5ab1b7380f2486c29cf6708954cdb5bbaa2d7798fd0103f845fa254da51a5e8'
LICENSE_SHA256 = 'fafba0527c3953c4b6e0e5b5739ba83612f8053bcdc9466730193cd1d590b408'
IDLE_OFFSET = 0x397d


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    original = SOURCE.read_bytes()
    license_bytes = SOURCE.with_name('license.key').read_bytes()
    if sha(original) != SOURCE_SHA256 or sha(license_bytes) != LICENSE_SHA256:
        raise SystemExit('Original firmware or license differs from the verified v1.72 pair')
    if struct.unpack_from('>I', original, 21)[0] != zlib.crc32(original[25:]):
        raise SystemExit('Original payload CRC32 is invalid')
    if original[IDLE_OFFSET - 4:IDLE_OFFSET + 4] != bytes.fromhex('fef902ac3008b208'):
        raise SystemExit('Original idle instruction context differs')
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
