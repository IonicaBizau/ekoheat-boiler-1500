#!/usr/bin/env python3
"""Verify the clock-only v1.73 image and an optional USB copy."""
import argparse
import hashlib
import json
import struct
import zlib
from pathlib import Path

SOURCE = Path('DTX9003 v1.73/DTX9003.uc3')
PACKAGE = Path('update-v1.73-no-clock')
SOURCE_SHA256 = 'e57bb9517c66e8f37ecb864daca5735bc14e3ef6a2614c94a962dc62809f2e3a'
OUTPUT_SHA256 = 'dec5a6496a4688258a0566d9b33cdf61f9497d18912310e097b71bf91972503e'
LICENSE_SHA256 = '8075e4bc145fadd645f7edfe2ec00c0b644b5a6edef3349531d5ff4cc155c3b5'
NAMES = {'DTX9003.uc3', 'license.key'}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_pair(directory, expected_image, expected_license, strict):
    directory = Path(directory)
    require(directory.is_dir() and not directory.is_symlink(), 'Package path is not a regular directory')
    extra = sorted(p.name for p in directory.iterdir() if p.name not in NAMES)
    if strict:
        require(not extra, 'Package has unexpected entries: ' + ', '.join(extra))
    for name, expected in [('DTX9003.uc3', expected_image), ('license.key', expected_license)]:
        target = directory / name
        require(target.is_file() and not target.is_symlink(), 'Missing or invalid ' + name)
        require(target.read_bytes() == expected, 'File contents differ: ' + name)
    return extra


def verify(update_dir=None):
    original = SOURCE.read_bytes()
    source_license = SOURCE.with_name('license.key').read_bytes()
    require(sha(original) == SOURCE_SHA256, 'Wrong stock v1.73 image')
    require(sha(source_license) == LICENSE_SHA256 and source_license == bytes.fromhex('341c'),
            'Wrong stock v1.73 license')
    require(len(original) == 453229 and original[:5] == b'AVR32', 'Wrong original wrapper or size')
    require(struct.unpack_from('>I', original, 21)[0] == zlib.crc32(original[25:]),
            'Original payload CRC32 mismatch')
    require(original[0x3aa3:0x3aab] == bytes.fromhex('fef902f23008b208'),
            'Wrong original idle instruction context')

    expected = bytearray(original)
    expected[0x3aa7:0x3aa9] = bytes.fromhex('3648')
    struct.pack_into('>I', expected, 21, zlib.crc32(expected[25:]))
    require(sha(expected) == OUTPUT_SHA256, 'Fixed expected image hash mismatch')
    extra_package = check_pair(PACKAGE, expected, source_license, strict=True)
    actual = (PACKAGE / 'DTX9003.uc3').read_bytes()
    require(struct.unpack_from('>I', actual, 21)[0] == zlib.crc32(actual[25:]),
            'Patched payload CRC32 mismatch')
    require(actual[0x3aa3:0x3aab] == bytes.fromhex('fef902f23648b208'),
            'Wrong patched idle instruction context')
    changed = [i for i, (before, after) in enumerate(zip(original, actual)) if before != after]
    require(set(changed) == {0x15, 0x16, 0x17, 0x18, 0x3aa7, 0x3aa8},
            'Unexpected changed bytes')
    require(actual[0xd149:0xd165] == original[0xd149:0xd165], 'Info label changed')
    require(actual[:21] == original[:21], 'Wrapper prefix changed')

    extra_usb = None
    if update_dir is not None:
        extra_usb = check_pair(update_dir, expected, source_license, strict=False)
    return {
        'status': 'PASS', 'image': str(PACKAGE / 'DTX9003.uc3'),
        'source_sha256': SOURCE_SHA256, 'output_sha256': OUTPUT_SHA256,
        'license_sha256': LICENSE_SHA256, 'size': len(actual),
        'crc32': '{:08X}'.format(zlib.crc32(actual[25:])),
        'changed_offsets': [hex(i) for i in changed],
        'info_version_unchanged': True, 'license_unchanged': True,
        'only_idle_instruction_and_crc_changed': True,
        'update_dir': str(update_dir) if update_dir is not None else None,
        'update_files_match': update_dir is not None,
        'extra_usb_entries': extra_usb, 'extra_package_entries': extra_package,
        'bootloader_acceptance_verified': False, 'hardware_execution': False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--update-dir', type=Path, help='Compare files copied to a mounted USB drive')
    args = parser.parse_args()
    try:
        result = verify(args.update_dir)
    except (OSError, ValueError) as error:
        raise SystemExit('FAIL: ' + str(error))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
